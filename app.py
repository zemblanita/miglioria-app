import streamlit as st
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

# 🔑 RECUPERO API KEY
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
if "cronologia" not in st.session_state:
    st.session_state.cronologia = []

if "ultimo_risultato" not in st.session_state:
    st.session_state.ultimo_risultato = None

if "ultima_voce" not in st.session_state:
    st.session_state.ultima_voce = ""

if "database_gare" not in st.session_state:
    st.session_state.database_gare = []

# ---------------------------------------------------------
# LOGO VETTORIALE SVG (MINIMAL M)
# ---------------------------------------------------------
SVG_LOGO_SIDEBAR = (
    '<svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M 22 80 V 30 L 50 62 L 90 18" stroke="#3b82f6" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>'
    '<path d="M 34 80 V 42 L 50 62 L 78 42 V 80" stroke="#ffffff" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>'
    '</svg>'
)

# ---------------------------------------------------------
# STILE CSS SICURO (JOIN DI STRINGHE BREVI)
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
    ".icon-badge { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 14px; font-size: 18px; }",
    ".badge-blue { background-color: #eff6ff; color: #2563eb; }",
    ".badge-green { background-color: #f0fdf4; color: #16a34a; }",
    ".badge-purple { background-color: #faf5ff; color: #9333ea; }",
    ".badge-orange { background-color: #fff7ed; color: #ea580c; }",
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
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.markdown(SVG_LOGO_SIDEBAR, unsafe_allow_html=True)
    with col_title:
        st.markdown("<h2 style='margin:0; padding:0; font-size:22px; font-weight:800; color:#ffffff;'>Miglior<span style='color:#3b82f6;'>IA</span></h2>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    menu = st.radio(
        "MENU",
        [
            "📄 Analisi capitolato", 
            "⏱️ Cronologia", 
            "📁 Archivio Gare & Training", 
            "⚖️ Stima Punteggio Gara"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 1px;'>CONFIGURAZIONE ENGINE</p>", unsafe_allow_html=True)
    
    modello_selezionato = st.selectbox(
        "Modello Groq:",
        options=modelli_disponibili,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 12px; color: #ffffff; opacity: 0.8;'><strong style='color: #ffffff;'>MigliorIA</strong><br>Piu valore alle tue gare.</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: ANALISI CAPITOLATO
# ---------------------------------------------------------
if menu == "📄 Analisi capitolato":

    st.markdown("<div class='welcome-text'>BENVENUTO SU</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Miglior<span>IA</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>L&#39;intelligenza artificiale al servizio delle tue gare d&#39;appalto. Analizza, migliora, ottimizza.</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='input-card-header'>📄 Voce di capitolato</div><div class='input-card-desc'>Incolla qui la voce di capitolato da analizzare.</div>", unsafe_allow_html=True)

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
            analizza_clicked = st.button("✨ ANALIZZA VOCE", use_container_width=True)

    if analizza_clicked:
        if not client:
            st.error("⚠️ API Key di Groq non trovata nei Secrets.")
        elif voce.strip():
            # RECUPERA I MIGLIORI ESEMPI DAL DATABASE DELLE GARE PER APPRENDERE LO STILE
            esempi_stile = ""
            gare_top = [g for g in st.session_state.database_gare if g.get("punteggio", 0) >= 8.0]
            if gare_top:
                esempi_stile = "\n\nIMPORTANTE: Imita lo stile tecnico e vincente delle nostre migliori gare passate:\n"
                for g in gare_top[:2]:
                    esempi_stile += f"--- ESEMPIO GARA VINCENTE (Voto {g['punteggio']}/10) ---\n{g['relazione'][:500]}...\n"

            prompt = (
                "Sei un esperto senior di capitolati tecnici e gare d'appalto nel settore delle costruzioni.\n"
                f"{esempi_stile}\n"
                f"Analizza la seguente voce di capitolato:\n{voce}\n\n"
                "Fornisci una risposta chiara, professionale e ben strutturata in Markdown:\n"
                "### 🔍 Requisiti e Prestazioni Principali\n"
                "### ⚠️ Criticità e Vincoli di Gara\n"
                "### 💡 Proposte di Miglioria Tecnico-Economica (almeno 5 punti)\n"
                "### 📦 Prodotti e Soluzioni Consigliate\n"
                "Proponi 3-4 marche/prodotti reali. IMPORTANTE: Trasforma il NOME di ciascun prodotto direttamente in un link di ricerca Google ordinario.\n"
                "Esempio formato: - **[Nome Prodotto / Brand](https://www.google.com/search?q=Nome+Prodotto+scheda+tecnica)**: descrizione breve.\n"
                "### 🌱 Conformità CAM (Criteri Ambientali Minimi)"
            )
            with st.spinner(f"Analisi in corso con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                        max_tokens=3000
                    )
                    risultato = chat_completion.choices[0].message.content
                    
                    st.session_state.ultimo_risultato = risultato
                    st.session_state.ultima_voce = voce

                    ora_corrente = datetime.now().strftime("%H:%M:%S")
                    st.session_state.cronologia.insert(0, {
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
        st.markdown("### 📊 Esito dell'Analisi Tecnica")
        st.markdown(st.session_state.ultimo_risultato)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='info-card'><div><div class='icon-badge badge-blue'>📄</div><h4>Analisi intelligente</h4><p>Estrai i requisiti, i vincoli e le criticita della voce di capitolato con l'AI.</p></div><div class='card-arrow'>→</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='info-card'><div><div class='icon-badge badge-green'>💡</div><h4>Migliorie su misura</h4><p>Ottieni proposte concrete per migliorare le prestazioni, la sostenibilita e il rapporto qualita/prezzo.</p></div><div class='card-arrow'>→</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='info-card'><div><div class='icon-badge badge-purple'>📦</div><h4>Prodotti e soluzioni</h4><p>Scopri soluzioni tecniche e prodotti compatibili con i requisiti di gara e i CAM.</p></div><div class='card-arrow'>→</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='info-card'><div><div class='icon-badge badge-orange'>⭐</div><h4>Confronta e scegli</h4><p>Metti a confronto le migliorie proposte per individuare la soluzione migliore.</p></div><div class='card-arrow'>→</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: CRONOLOGIA
# ---------------------------------------------------------
elif menu == "⏱️ Cronologia":
    st.markdown("## ⏱️ Cronologia Analisi")
    st.markdown("<div class='main-subtitle'>Consulta o riapri le analisi effettuate durante questa sessione.</div>", unsafe_allow_html=True)

    if not st.session_state.cronologia:
        st.info("Nessuna analisi salvata nella sessione corrente.")
    else:
        col_list, col_clear = st.columns([4, 1])
        with col_clear:
            if st.button("🗑️ Svuota Cronologia", use_container_width=True):
                st.session_state.cronologia = []
                st.session_state.ultimo_risultato = None
                st.session_state.ultima_voce = ""
                st.rerun()

        st.divider()

        for idx, item in enumerate(st.session_state.cronologia):
            with st.container():
                st.markdown("<div class='history-card'>", unsafe_allow_html=True)
                st.markdown(f"**⏰ Ora:** {item['ora']}")
                st.markdown(f"**📄 Voce analizzata:** _{item['voce'][:120]}..._" if len(item['voce']) > 120 else f"**📄 Voce analizzata:** _{item['voce']}_")
                
                num_analisi = len(st.session_state.cronologia) - idx
                if st.button(f"🔗 Visualizza Analisi #{num_analisi}", key=f"btn_cron_{idx}", type="tertiary"):
                    st.session_state.ultimo_risultato = item['risultato']
                    st.session_state.ultima_voce = item['voce']
                    st.success("Analisi ricaricata! Passa alla scheda '📄 Analisi capitolato' per consultarla.")

                st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: ARCHIVIO GARE & TRAINING AI
# ---------------------------------------------------------
elif menu == "📁 Archivio Gare & Training":
    st.markdown("## 📁 Archivio Gare & Training AI")
    st.markdown("<div class='main-subtitle'>Inserisci le tue gare passate e i punteggi ricevuti per allenare l'IA sul tuo stile vincente.</div>", unsafe_allow_html=True)

    with st.expander("➕ Inserisci una Nuova Gara nell'Archivio", expanded=True):
        nome_gara = st.text_input("Oggetto / Nome della Gara", placeholder="Es. Riqualificazione Scuola Primaria...")
        relazione_gara = st.text_area("Testo / Relazione della Miglioria Presentata", height=150, placeholder="Incolla qui la miglioria o la relazione tecnica utilizzata...")
        punteggio_gara = st.slider("Punteggio Tecnico Ottenuto (da 0 a 10)", min_value=0.0, max_value=10.0, value=8.5, step=0.1)
        
        if st.button("💾 Salva Gara nel Database"):
            if nome_gara.strip() and relazione_gara.strip():
                st.session_state.database_gare.append({
                    "id": len(st.session_state.database_gare) + 1,
                    "nome": nome_gara,
                    "relazione": relazione_gara,
                    "punteggio": punteggio_gara
                })
                st.success(f"Gara '{nome_gara}' salvata con successo! L'IA ne terrà conto nelle prossime risposte.")
            else:
                st.warning("Compila sia il nome che il testo della relazione.")

    st.divider()
    st.markdown("### 📚 Database Gare Archiviate")

    if not st.session_state.database_gare:
        st.info("Nessuna gara salvata finora. Aggiungi la tua prima gara per iniziare il training dell'IA!")
    else:
        for idx, g in enumerate(st.session_state.database_gare):
            with st.container():
                st.markdown(f"<div class='history-card'>", unsafe_allow_html=True)
                col_g1, col_g2 = st.columns([3, 1])
                with col_g1:
                    st.markdown(f"### 🏆 {g['nome']}")
                    st.markdown(f"_{g['relazione'][:200]}..._")
                with col_g2:
                    st.metric("Punteggio Tecnico", f"{g['punteggio']}/10")
                    
                    # Aggiornamento punteggio
                    nuovo_voto = st.number_input("Aggiorna Voto", min_value=0.0, max_value=10.0, value=float(g['punteggio']), step=0.1, key=f"voto_{idx}")
                    if nuovo_voto != g['punteggio']:
                        st.session_state.database_gare[idx]['punteggio'] = nuovo_voto
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEZIONE: STIMA PUNTEGGIO GARA
# ---------------------------------------------------------
elif menu == "⚖️ Stima Punteggio Gara":
    st.markdown("## ⚖️ Stima Punteggio Offerta Tecnica")
    st.markdown("<div class='main-subtitle'>Valuta in anteprima il punteggio tecnico che la commissione potrebbe assegnare alla tua miglioria.</div>", unsafe_allow_html=True)

    with st.container():
        miglioria_input = st.text_area("Miglioria Proposta da Valutare", height=150, placeholder="Incolla qui la soluzione tecnica o la miglioria che intendi proporre...")
        criteri_input = st.text_input("Criteri di Valutazione / Disciplinare (Opzionale)", placeholder="Es. Criterio 2.1: Sostenibilità ambientale e risparmio energetico (Max 15 pt)")
        
        if st.button("🎯 CALCOLA STIMA PUNTEGGIO"):
            if miglioria_input.strip():
                prompt_stima = f"""
Sei un Commissario di Gara senior esperto nella valutazione di Offerte Tecniche.

Miglioria Proposta:
{miglioria_input}

Criteri di Gara / Disciplinare:
{criteri_input if criteri_input else 'Criteri standard di valutazione dell offerta economicamente piu vantaggiosa.'}

Fornisci un report strutturato in Markdown:
### 📊 Stima Punteggio Ipotetico (es. 8.5/10)
### 🌟 Punti di Forza (perche la commissione assegnera punti)
### ⚠️ Punti Deboli o Rischi di Contesto
### 💡 Consigli di Redazione per Massimizzare il Punteggio
"""
                with st.spinner("Valutazione in corso con l AI..."):
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt_stima}],
                            model=modello_selezionato,
                            temperature=0.2,
                            max_tokens=2000
                        )
                        st.session_state.risultato_punteggio = chat_completion.choices[0].message.content
                    except Exception as e:
                        st.error(f"Errore durante l elaborazione: {e}")
            else:
                st.warning("Inserisci la descrizione della miglioria prima di procedere.")

    if "risultato_punteggio" in st.session_state and st.session_state.risultato_punteggio:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown("### 📊 Report della Commissione AI")
        st.markdown(st.session_state.risultato_punteggio)
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer-container'><div>MigliorIA | AI per gare d'appalto</div><div><span class='status-dot'></span>Sistema attivo</div></div>", unsafe_allow_html=True)