import streamlit as st
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

# Inizializzazione Session State per salvare l'ultimo risultato
if "ultimo_risultato" not in st.session_state:
    st.session_state.ultimo_risultato = None

# ---------------------------------------------------------
# LOGO SVG VETTORIALE (MINIMAL M)
# ---------------------------------------------------------
SVG_LOGO_SIDEBAR = """
<svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M 22 80 V 30 L 50 62 L 90 18" stroke="#3b82f6" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>
    <path d="M 34 80 V 42 L 50 62 L 78 42 V 80" stroke="#ffffff" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>
</svg>
"""

# ---------------------------------------------------------
# STILE CSS REPLICATO DAL MOCKUP
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #f3f4f6;
        color: #111827;
    }

    [data-testid="stSidebar"] {
        background-color: #0b1329 !important;
        padding-top: 24px;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 10px !important;
        color: #ffffff !important;
    }

    .welcome-text {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #9ca3af;
        margin-bottom: 2px;
        text-transform: uppercase;
    }

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #111827;
        margin: 0;
        line-height: 1.1;
    }
    .main-title span {
        color: #2563eb;
    }

    .main-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-top: 6px;
        margin-bottom: 24px;
    }

    .input-card-header {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }

    .input-card-desc {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 16px;
    }

    .stTextArea textarea {
        background-color: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        color: #111827 !important;
        font-size: 14px !important;
    }
    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    div.stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
    }

    /* Container Risultato */
    .result-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 28px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-top: 20px;
        margin-bottom: 30px;
    }

    .info-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e5e7eb;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .icon-badge {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
        font-size: 18px;
    }
    .badge-blue { background-color: #eff6ff; color: #2563eb; }
    .badge-green { background-color: #f0fdf4; color: #16a34a; }
    .badge-purple { background-color: #faf5ff; color: #9333ea; }
    .badge-orange { background-color: #fff7ed; color: #ea580c; }

    .info-card h4 {
        font-size: 15px;
        font-weight: 700;
        color: #111827;
        margin: 0 0 6px 0;
    }

    .info-card p {
        font-size: 12px;
        color: #6b7280;
        margin: 0 0 16px 0;
        line-height: 1.4;
    }

    .card-arrow {
        font-size: 16px;
        color: #9ca3af;
    }

    .footer-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
        padding-top: 16px;
        border-top: 1px solid #e5e7eb;
        font-size: 12px;
        color: #9ca3af;
    }
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

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
            "📁 File salvati", 
            "⚖️ Confronta le migliorie"
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
    st.markdown("""
        <div style='font-size: 12px; color: #ffffff; opacity: 0.8;'>
            <strong style='color: #ffffff;'>MigliorIA</strong><br>
            Più valore alle tue gare.
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------
if menu == "📄 Analisi capitolato":

    # Header principale
    st.markdown("<div class='welcome-text'>BENVENUTO SU</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Miglior<span>IA</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>L'intelligenza artificiale al servizio delle tue gare d'appalto. Analizza, migliora, ottimizza.</div>", unsafe_allow_html=True)

    # Card principale Voce di Capitolato
    with st.container():
        st.markdown("""
            <div class='input-card-header'>📄 Voce di capitolato</div>
            <div class='input-card-desc'>Incolla qui la voce di capitolato da analizzare.</div>
        """, unsafe_allow_html=True)

        voce = st.text_area(
            "Voce di capitolato input",
            height=160,
            placeholder='Esempio: "Fornitura e posa di unità di climatizzazione con caratteristiche..."',
            label_visibility="collapsed"
        )

        col_char, col_btn = st.columns([2, 1])
        with col_char:
            st.caption(f"{len(voce)}/10000")
        with col_btn:
            analizza_clicked = st.button("✨ ANALIZZA VOCE", use_container_width=True)

    # Logica di Elaborazione
    if analizza_clicked:
        if not client:
            st.error("⚠️ API Key di Groq non trovata nei Secrets.")
        elif voce.strip():
            prompt = f"""
Sei un esperto senior di capitolati tecnici e gare d'appalto nel settore delle costruzioni.

Analizza la seguente voce di capitolato:
{voce}

Fornisci una risposta chiara, professionale e ben strutturata in Markdown:
### 🔍 Requisiti e Prestazioni Principali
### ⚠️ Criticità e Vincoli di Gara
### 💡 Proposte di Miglioria Tecnico-Economica (almeno 5 punti)
### 📦 Prodotti e Soluzioni Consigliate (con suggerimenti sui marchi/tipologie e link di ricerca)
### 🌱 Conformità CAM (Criteri Ambientali Minimi)
"""
            with st.spinner(f"Analisi in corso con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                        max_tokens=1000
                    )
                    # Salviamo il risultato nella sessione
                    st.session_state.ultimo_risultato = chat_completion.choices[0].message.content

                except Exception as e:
                    st.error(f"Errore durante l'elaborazione API: {e}")
        else:
            st.warning("Inserisci una voce di capitolato per procedere.")

    # MOSTRA IL RISULTATO SALVATO NELLO STATE
    if st.session_state.ultimo_risultato:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown("### 📊 Esito dell'Analisi Tecnica")
        st.markdown(st.session_state.ultimo_risultato)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # 4 Cards Informative
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-blue'>📄</div>
                    <h4>Analisi intelligente</h4>
                    <p>Estrai i requisiti, i vincoli e le criticità della voce di capitolato con l'AI.</p>
                </div>
                <div class='card-arrow'>→</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-green'>💡</div>
                    <h4>Migliorie su misura</h4>
                    <p>Ottieni proposte concrete per migliorare le prestazioni, la sostenibilità e il rapporto qualità/prezzo.</p>
                </div>
                <div class='card-arrow'>→</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
            <div class='info-card'>
                <div>
                    <div class='icon-badge badge-purple'>📦</div>