import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from groq import Groq

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MigliorIA - AI per Gare d'Appalto",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# GESTIONE DATABASE SQLITE
# ---------------------------------------------------------
DB_FILE = "miglioria.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabella Utenti
    c.execute('''
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Tabella Gare Utente
    c.execute('''
        CREATE TABLE IF NOT EXISTS gare (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            relazione TEXT NOT NULL,
            punteggio REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES utenti(id)
        )
    ''')
    # Tabella Cronologia Utente (Permanente)
    c.execute('''
        CREATE TABLE IF NOT EXISTS cronologia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ora TEXT NOT NULL,
            voce TEXT NOT NULL,
            risultato TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES utenti(id)
        )
    ''')
    conn.commit()
    conn.close()

def make_hash(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'miglioria_salt', 100000).hex()

def register_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO utenti (username, password_hash) VALUES (?, ?)", (username, make_hash(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username FROM utenti WHERE username = ? AND password_hash = ?", (username, make_hash(password)))
    user = c.fetchone()
    conn.close()
    return user

def salva_gara_db(user_id, nome, relazione, punteggio):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO gare (user_id, nome, relazione, punteggio) VALUES (?, ?, ?, ?)", (user_id, nome, relazione, punteggio))
    conn.commit()
    conn.close()

def get_gare_db(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nome, relazione, punteggio FROM gare WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "nome": r[1], "relazione": r[2], "punteggio": r[3]} for r in rows]

def update_voto_gara_db(gara_id, nuovo_punteggio):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE gare SET punteggio = ? WHERE id = ?", (nuovo_punteggio, gara_id))
    conn.commit()
    conn.close()

def salva_cronologia_db(user_id, ora, voce, risultato):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO cronologia (user_id, ora, voce, risultato) VALUES (?, ?, ?, ?)", (user_id, ora, voce, risultato))
    conn.commit()
    conn.close()

def get_cronologia_db(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, ora, voce, risultato FROM cronologia WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "ora": r[1], "voce": r[2], "risultato": r[3]} for r in rows]

def svuota_cronologia_db(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM cronologia WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# RECUPERO API KEY & GROQ
# ---------------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

client = None
modelli_disponibili = []

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.models.list()
        tutti_modelli = [m.id for m in response.data]
        
        modelli_disponibili = [
            m for m in tutti_modelli 
            if not any(banned in m.lower() for banned in ["whisper", "guard", "orpheus", "safetensors", "preview", "qwen"])
        ]
        modelli_disponibili.sort(
            key=lambda x: (
                "llama-3.3-70b" in x.lower(),
                "llama-3.1-70b" in x.lower(),
                "llama-3.1" in x.lower(),
                "llama" in x.lower()
            ), 
            reverse=True
        )
    except Exception:
        pass

if not modelli_disponibili:
    modelli_disponibili = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

# ---------------------------------------------------------
# INITIALIZE SESSION STATES
# ---------------------------------------------------------
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

if "cronologia_ospite" not in st.session_state:
    st.session_state.cronologia_ospite = []

if "ultimo_risultato" not in st.session_state:
    st.session_state.ultimo_risultato = None

if "ultima_voce" not in st.session_state:
    st.session_state.ultima_voce = ""

if "mostra_auth_box" not in st.session_state:
    st.session_state.mostra_auth_box = False

# ---------------------------------------------------------
# SYSTEM PROMPT AVANZATO (NORMATIVA & CAM ITALIA)
# ---------------------------------------------------------
SYSTEM_PROMPT_MIGLIORIA = """
Sei "MigliorIA Engine", il sistema di Intelligenza Artificiale specializzato nell'analisi di capitolati e nella redazione di offerte tecniche per gare d'appalto pubbliche in Italia.

INDIRIZZO NORMATIVO E TECNICO:
1. NORMATIVA DI RIFERIMENTO: Operi in conformità al Codice dei Contratti Pubblici italiano (D.Lgs. 36/2023), valorizzando il "Principio del Risultato" (Art. 1) e il "Principio di Fiducia" (Art. 2).
2. CRITERI AMBIENTALI MINIMI (CAM): Ogni proposta deve essere strettamente allineata al D.M. 23 giugno 2022 (CAM Edilizia/Costruzioni e successive integrazioni). Fai riferimenti specifici a:
   - Materia riciclata o recuperata e contenuto minimo di riciclato.
   - Disassemblabilità e demolizione selettiva a fine vita.
   - Prestazioni energetiche dell'involucro e degli impianti (LCC - Life Cycle Costing).
   - Emissioni indoor (VOC) ed ecocompatibilità dei materiali.
3. TONO E STILE: Linguaggio tecnico rigido, formale, persuasivo per la commissione giudicatrice. Utilizza terminologia appropriata (es. "variante migliorativa", "prestazioni sopralimite", "riduzione degli impatti di cantiere", "durabilità operativa").
4. OBIETTIVO STRATEGICO: Massimizzare il punteggio nell'Offerta Economicamente Più Vantaggiosa (OEPV) dimostrando valore aggiunto concreto senza alterare gli elementi essenziali non modificabili del progetto.
"""

def genera_risposta_llm(messages_list, modello_preferito):
    try:
        completion = client.chat.completions.create(
            messages=messages_list,
            model=modello_preferito,
            temperature=0.2,
            max_tokens=3500
        )
        return completion.choices[0].message.content
    except Exception as primary_error:
        for alt_model in modelli_disponibili:
            if alt_model != modello_preferito:
                try:
                    completion = client.chat.completions.create(
                        messages=messages_list,
                        model=alt_model,
                        temperature=0.2,
                        max_tokens=3500
                    )
                    return completion.choices[0].message.content
                except Exception:
                    continue
        raise primary_error

# ---------------------------------------------------------
# LOGO VETTORIALE SVG
# ---------------------------------------------------------
SVG_LOGO_SIDEBAR = (
    '<svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M 22 80 V 30 L 50 62 L 90 18" stroke="#3b82f6" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>'
    '<path d="M 34 80 V 42 L 50 62 L 78 42 V 80" stroke="#ffffff" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>'
    '</svg>'
)

# ---------------------------------------------------------
# STILE CSS SICURO
# ---------------------------------------------------------
css_lines = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');",
    "html, body, [class*='css'] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }",
    ".stApp { background-color: #f3f4f6; color: #111827; }",
    "[data-testid='stSidebar'] { background-color: #0b1329 !important; padding-top: 24px; }",
    "[data-testid='stSidebar'] * { color: #ffffff !important; }",
    "[data-testid='stSidebar'] .stRadio label { font-size: 14px !important; font-weight: 500 !important; padding: 8px 10px !important; color: #ffffff !important; }",
    ".welcome-text { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #9ca3af; margin-bottom: 2px; text-transform: uppercase; }",
    ".main-title { font-size: 38px; font-weight: 800; color: #111827; margin: 0; line-height: 1.1; }",
    ".main-title span { color: #2563eb; }",
    ".main-subtitle { font-size: 14px; color: #6b7280; margin-top: 6px; margin-bottom: 24px; }",
    ".input-card-header { font-size: 18px; font-weight: 700; color: #111827; display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }",
    ".input-card-desc { font-size: 13px; color: #6b7280; margin-bottom: 16px; }",
    ".stTextArea textarea { background-color: #f9fafb !important; border: 1px solid #e5e7eb !important; border-radius: 10px !important; color: #111827 !important; font-size: 14px !important; }",
    ".stTextArea textarea:focus { border-color: #2563eb !important; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important; }",
    "div.stButton > button { background-color: #2563eb !important; color: #ffffff !important; font-weight: 600 !important; font-size: 13px !important; letter-spacing: 0.5px !important; border-radius: 10px !important; padding: 10px 24px !important; border: none !important; box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important; }",
    "div.stButton > button:hover { background-color: #1d4ed8 !important; }",
    ".result-container { background-color: #ffffff; border-radius: 16px; padding: 28px; border: 1px solid #e5e7eb; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-top: 20px; margin-bottom: 30px; }",
    ".info-card { background-color: #ffffff; border-radius: 14px; padding: 20px; border: 1px solid #e5e7eb; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }",
    ".icon-badge { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }",
    ".badge-blue { background-color: #eff6ff; fill: #2563eb; }",
    ".badge-green { background-color: #f0fdf4; fill: #16a34a; }",
    ".badge-purple { background-color: #faf5ff; fill: #9333ea; }",
    ".badge-orange { background-color: #fff7ed; fill: #ea580c; }",
    ".info-card h4 { font-size: 15px; font-weight: 700; color: #111827; margin: 0 0 6px 0; }",
    ".info-card p { font-size: 12px; color: #6b7280; margin: 0 0 16px 0; line-height: 1.4; }",
    ".card-arrow { font-size: 16px; color: #9ca3af; }",
    ".history-card { background-color: #ffffff; border-radius: 12px; padding: 18px; border: 1px solid #e5e7eb; margin-bottom: 12px; }",
    ".footer-container { display: flex; justify-content: space-between; align-items: center; margin-top: 30px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af; }",
    ".status-dot { height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 6px; }",
    "</style>"
]
CSS_STYLE = "".join(css_lines)

st.markdown(CSS_STYLE, unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER TOP BAR (ACCEDI / REGISTRATI IN ALTO A DESTRA)
# ---------------------------------------------------------
col_top_space, col_top_auth = st.columns([3, 1])

with col_top_auth:
    if st.session_state.logged_user:
        st.markdown(f"<div style='text-align:right; font-size:13px; color:#374151; padding-top:8px;'>Account: <strong>{st.session_state.logged_user['username']}</strong></div>", unsafe_allow_html=True)
        if st.button("Logout", key="btn_top_logout", type="tertiary"):
            st.session_state.logged_user = None
            st.rerun()
    else:
        if st.button("Accedi | Registrati", key="btn_top_login"):
            st.session_state.mostra_auth_box = not st.session_state.mostra_auth_box

# MODALE / SCHEDA AUTHENTICATION
if not st.session_state.logged_user and st.session_state.mostra_auth_box:
    st.markdown("<div class='result-container' style='padding:24px; border:1px solid #2563eb;'>", unsafe_allow_html=True)
    st.markdown("### Autenticazione Piattaforma")
    st.markdown("<p style='font-size:13px; color:#6b7280;'>Accedi per salvare in modo permanente le tue analisi e allenare l'IA con le tue gare passate.</p>", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["Accedi", "Registrati"])
    
    with tab_login:
        user_login = st.text_input("Username", key="l_user")
        pass_login = st.text_input("Password", type="password", key="l_pass")
        if st.button("ACCEDI ALL'ACCOUNT", use_container_width=True):
            account = login_user(user_login.strip(), pass_login)
            if account:
                st.session_state.logged_user = {"id": account[0], "username": account[1]}
                st.session_state.mostra_auth_box = False
                st.success("Autenticazione completata con successo.")
                st.rerun()
            else:
                st.error("Credenziali non valide. Riprova.")

    with tab_register:
        user_reg = st.text_input("Scegli Username", key="r_user")
        pass_reg = st.text_input("Scegli Password", type="password", key="r_pass")
        if st.button("CREA NUOVO ACCOUNT", use_container_width=True):
            if user_reg.strip() and pass_reg:
                if register_user(user_reg.strip(), pass_reg):
                    st.success("Account registrato con successo. Ora e possibile effettuare l'accesso.")
                else:
                    st.error("Username gia in uso. Selezionare un nome alternativo.")
            else:
                st.warning("Compilare tutti i campi richiesti.")
                
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.markdown(SVG_LOGO_SIDEBAR, unsafe_allow_html=True)
    with col_title:
        st.markdown("<h2 style='margin:0; padding:0; font-size:22px; font-weight:800; color:#ffffff;'>Miglior<span style='color:#3b82f6;'>IA</span></h2>", unsafe_allow_html=True)

    if st.session_state.logged_user:
        st.markdown(f"<p style='font-size:12px; color:#9ca3af; margin-top:8px;'>Account attivo: <strong style='color:#ffffff;'>{st.session_state.logged_user['username']}</strong></p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:12px; color:#9ca3af; margin-top:8px;'>Modalita Ospite</p>", unsafe_allow_html=True)

    menu = st.radio(
        "MENU",
        [
            "Analisi capitolato", 
            "Cronologia", 
            "Archivio Gare & Training", 
            "Stima Punteggio Gara"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 1px;'>ENGINE SELEZIONATO</p>", unsafe_allow_html=True)
    
    modello_selezionato = st.selectbox(
        "Modello Groq:",
        options=modelli_disponibili,
        index=0,
        label_visibility="collapsed"
    )

# ---------------------------------------------------------
# SEZIONE: ANALISI CAPITOLATO (LIBERA A TUTTI)
# ---------------------------------------------------------
if menu == "Analisi capitolato":

    st.markdown("<div class='welcome-text'>BENVENUTO SU</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Miglior<span>IA</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>L&#39;intelligenza artificiale al servizio delle tue gare d&#39;appalto. Analizza, migliora, ottimizza.</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='input-card-header'>Voce di capitolato</div><div class='input-card-desc'>Incolla qui la voce di capitolato da analizzare.</div>", unsafe_allow_html=True)

        voce = st.text_area(
            "Voce di capitolato input",
            value=st.session_state.ultima_voce,
            height=160,
            placeholder='Esempio: "Fornitura e posa di unita di climatizzazione con caratteristiche..."',
            label_visibility="collapsed"
        )

        col_char, col_btn = st.columns([2, 1])
        with col_char:
            st.caption(f"{len(voce)}/10000")
        with col_btn:
            analizza_clicked = st.button("ANALIZZA VOCE", use_container_width=True)

    if analizza_clicked:
        if not client:
            st.error("API Key di Groq non trovata nei Secrets.")
        elif voce.strip():
            esempi_stile = ""
            
            # Se l'utente è loggato, recupera le sue gare top dal DB per personalizzare la risposta
            if st.session_state.logged_user:
                user_id = st.session_state.logged_user["id"]
                gare_utente = get_gare_db(user_id)
                gare_top = [g for g in gare_utente if g["punteggio"] >= 8.0]
                if gare_top:
                    esempi_stile = "\n\nMODELLO DI STILE E STRUTTURA (Imita le migliori gare dell'utente):\n"
                    for g in gare_top[:2]:
                        esempi_stile += f"--- ESEMPIO VINCENTE UTENTE (Punteggio {g['punteggio']}/10) ---\n{g['relazione'][:600]}...\n"

            user_prompt = (
                f"{esempi_stile}\n"
                f"Analizza con approccio tecnico avanzato la seguente voce di capitolato:\n{voce}\n\n"
                "Fornisci una risposta chiara, professionale e ben strutturata in Markdown:\n"
                "### Requisiti e Prestazioni Principali\n"
                "### Criticita e Vincoli di Gara (con quadro dei rischi)\n"
                "### Proposte di Miglioria Tecnico-Economica (almeno 5 punti operativi)\n"
                "### Prodotti e Soluzioni Consigliate\n"
                "Proponi 3-4 marche/prodotti reali. IMPORTANTE: Trasforma il NOME di ciascun prodotto direttamente in un link di ricerca Google ordinario.\n"
                "Esempio formato: - **[Nome Prodotto / Brand](https://www.google.com/search?q=Nome+Prodotto+scheda+tecnica)**: descrizione breve.\n"
                "### Conformita CAM (Criteri Ambientali Minimi D.M. 23/06/2022)"
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT_MIGLIORIA},
                {"role": "user", "content": user_prompt}
            ]

            with st.spinner(f"Elaborazione in corso con {modello_selezionato}..."):
                try:
                    risultato = genera_risposta_llm(messages, modello_selezionato)
                    
                    st.session_state.ultimo_risultato = risultato
                    st.session_state.ultima_voce = voce

                    ora_corrente = datetime.now().strftime("%H:%M:%S")
                    
                    # Salva su DB se loggato, altrimenti in memoria ospite
                    if st.session_state.logged_user:
                        salva_cronologia_db(st.session_state.logged_user["id"], ora_corrente, voce, risultato)
                    else:
                        st.session_state.cronologia_ospite.insert(0, {
                            "ora": ora_corrente,
                            "voce": voce,
                            "risultato": risultato
                        })

                except Exception as e:
                    st.error(f"Errore durante l'elaborazione API: {e}")
        else:
            st.warning("Inserisci una voce di capitolato per procedere.")

    if st.session_state.ultimo_risultato:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown("### Esito dell'Analisi Tecnica")
        st.markdown(st.session_state.ultimo_risultato)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-blue'>
                        <svg width="18" height="18" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                    </div>
                    <h4>Analisi intelligente</h4>
                    <p>Estrai i requisiti, i vincoli e le criticita della voce di capitolato con l'AI.</p>
                </div>
                <div class='card-arrow'>→</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-green'>
                        <svg width="18" height="18" viewBox="0 0 24 24"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z"/></svg>
                    </div>
                    <h4>Migliorie su misura</h4>
                    <p>Ottieni proposte concrete per migliorare le prestazioni, la sostenibilita e il rapporto qualita/prezzo.</p>
                </div>
                <div class='card-arrow'>→</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-purple'>
                        <svg width="18" height="18" viewBox="0 0 24 24"><path d="M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z"/></svg>
                    </div>
                    <h4>Prodotti e soluzioni</h4>
                    <p>Scopri soluzioni tecniche e prodotti compatibili con i requisiti di gara e i CAM.</p>
                </div>
                <div class='card-arrow'>→</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-orange'>
                        <svg width="18" height="18" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
                    </div>
                    <h4>Confronta e scegli</h4>
                    <p>Metti a confronto le migliorie proposte per individuare la soluzione migliore.</p>
                </div>
                <div class='card-arrow'>→</div>
            </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: CRONOLOGIA (PERMANENTE PER UTENTI LOGGATI)
# ---------------------------------------------------------
elif menu == "Cronologia":
    st.markdown("## Cronologia Analisi")
    
    if st.session_state.logged_user:
        st.markdown(f"<div class='main-subtitle'>Cronologia permanente salvata nel tuo account (<strong>{st.session_state.logged_user['username']}</strong>).</div>", unsafe_allow_html=True)
        cronologia_lista = get_cronologia_db(st.session_state.logged_user["id"])
    else:
        st.markdown("<div class='main-subtitle'>Cronologia temporanea della sessione ospite (Effettua l'accesso per salvarla in modo permanente).</div>", unsafe_allow_html=True)
        cronologia_lista = st.session_state.cronologia_ospite

    if not cronologia_lista:
        st.info("Nessuna analisi salvata finora.")
    else:
        col_list, col_clear = st.columns([4, 1])
        with col_clear:
            if st.button("Svuota Cronologia", use_container_width=True):
                if st.session_state.logged_user:
                    svuota_cronologia_db(st.session_state.logged_user["id"])
                else:
                    st.session_state.cronologia_ospite = []
                st.session_state.ultimo_risultato = None
                st.session_state.ultima_voce = ""
                st.rerun()

        st.divider()

        for idx, item in enumerate(cronologia_lista):
            with st.container():
                st.markdown("<div class='history-card'>", unsafe_allow_html=True)
                st.markdown(f"**Ora:** {item['ora']}")
                st.markdown(f"**Voce analizzata:** _{item['voce'][:120]}..._" if len(item['voce']) > 120 else f"**Voce analizzata:** _{item['voce']}_")
                
                num_analisi = len(cronologia_lista) - idx
                if st.button(f"Visualizza Analisi #{num_analisi}", key=f"btn_cron_{idx}", type="tertiary"):
                    st.session_state.ultimo_risultato = item['risultato']
                    st.session_state.ultima_voce = item['voce']
                    st.success("Analisi ricaricata! Passa alla scheda 'Analisi capitolato' per consultarla.")

                st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: ARCHIVIO GARE & TRAINING (RICHIEDE LOGIN)
# ---------------------------------------------------------
elif menu == "Archivio Gare & Training":
    st.markdown("## Archivio Gare & Training AI")
    
    if not st.session_state.logged_user:
        st.warning("Per accedere all'Archivio Gare e allenare l'IA sul tuo stile e necessario effettuare l'accesso.")
        st.info("Clicca in alto a destra su 'Accedi | Registrati' per entrare nel tuo account.")
    else:
        user_id = st.session_state.logged_user["id"]
        username = st.session_state.logged_user["username"]
        
        st.markdown("<div class='main-subtitle'>Inserisci le tue gare passate per salvarle in modo permanente nel tuo account.</div>", unsafe_allow_html=True)

        with st.expander("Inserisci una Nuova Gara nel tuo Archivio", expanded=True):
            nome_gara = st.text_input("Oggetto / Nome della Gara", placeholder="Es. Riqualificazione Scuola Primaria...")
            relazione_gara = st.text_area("Testo / Relazione della Miglioria Presentata", height=150, placeholder="Incolla qui la miglioria o la relazione tecnica utilizzata...")
            punteggio_gara = st.slider("Punteggio Tecnico Ottenuto (da 0 a 10)", min_value=0.0, max_value=10.0, value=8.5, step=0.1)
            
            if st.button("Salva Gara nel Database Permanente"):
                if nome_gara.strip() and relazione_gara.strip():
                    salva_gara_db(user_id, nome_gara.strip(), relazione_gara.strip(), punteggio_gara)
                    st.success(f"Gara '{nome_gara}' salvata permanentemente nel tuo account.")
                    st.rerun()
                else:
                    st.warning("Compila sia il nome che il testo della relazione.")

        st.divider()
        st.markdown(f"### Le tue Gare Archiviate ({username})")

        database_gare_utente = get_gare_db(user_id)

        if not database_gare_utente:
            st.info("Nessuna gara salvata finora nel tuo account. Aggiungi la tua prima gara per iniziare.")
        else:
            for idx, g in enumerate(database_gare_utente):
                with st.container():
                    st.markdown("<div class='history-card'>", unsafe_allow_html=True)
                    col_g1, col_g2 = st.columns([3, 1])
                    with col_g1:
                        st.markdown(f"### {g['nome']}")
                        st.markdown(f"_{g['relazione'][:200]}..._")
                    with col_g2:
                        st.metric("Punteggio Tecnico", f"{g['punteggio']}/10")
                        nuovo_voto = st.number_input("Aggiorna Voto", min_value=0.0, max_value=10.0, value=float(g['punteggio']), step=0.1, key=f"db_voto_{g['id']}")
                        if nuovo_voto != g['punteggio']:
                            update_voto_gara_db(g['id'], nuovo_voto)
                            st.success("Voto aggiornato.")
                            st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: STIMA PUNTEGGIO GARA
# ---------------------------------------------------------
elif menu == "Stima Punteggio Gara":
    st.markdown("## Stima Punteggio Offerta Tecnica")
    st.markdown("<div class='main-subtitle'>Valuta in anteprima il punteggio tecnico che la commissione potrebbe assegnare alla tua miglioria.</div>", unsafe_allow_html=True)

    with st.container():
        miglioria_input = st.text_area("Miglioria Proposta da Valutare", height=150, placeholder="Incolla qui la soluzione tecnica o la miglioria che intendi proporre...")
        criteri_input = st.text_input("Criteri di Valutazione / Disciplinare (Opzionale)", placeholder="Es. Criterio 2.1: Sostenibilita ambientale e risparmio energetico (Max 15 pt)")
        
        if st.button("CALCOLA STIMA PUNTEGGIO"):
            if miglioria_input.strip():
                user_prompt_stima = f"""
Miglioria Proposta:
{miglioria_input}

Criteri di Gara / Disciplinare:
{criteri_input if criteri_input else 'Criteri standard di valutazione dell offerta economicamente piu vantaggiosa.'}

Fornisci un report giudizioso in Markdown:
### Stima Punteggio Ipotetico (es. 8.5/10)
### Punti di Forza (elementi di premialita per la commissione)
### Punti Deboli o Rischi di Contesto
### Consigli di Redazione per Massimizzare il Punteggio
"""
                messages_stima = [
                    {"role": "system", "content": SYSTEM_PROMPT_MIGLIORIA},
                    {"role": "user", "content": user_prompt_stima}
                ]
                with st.spinner("Valutazione in corso con l AI..."):
                    try:
                        st.session_state.risultato_punteggio = genera_risposta_llm(messages_stima, modello_selezionato)
                    except Exception as e:
                        st.error(f"Errore durante l'elaborazione: {e}")
            else:
                st.warning("Inserisci la descrizione della miglioria prima di procedere.")

    if "risultato_punteggio" in st.session_state and st.session_state.risultato_punteggio:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown("### Report della Commissione AI")
        st.markdown(st.session_state.risultato_punteggio)
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer-container'><div>MigliorIA | AI per gare d'appalto</div><div><span class='status-dot'></span>Sistema attivo</div></div>", unsafe_allow_html=True)