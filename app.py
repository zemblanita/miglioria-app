import streamlit as st
import json
from groq import Groq

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MigliorIA",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔑 RECUPERO SICURO API KEY
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
            if not any(banned in m.lower() for banned in ["whisper", "guard", "orpheus", "safetensors", "preview"])
        ]
        modelli_disponibili.sort(key=lambda x: ("llama" in x.lower(), x), reverse=True)
    except Exception:
        pass

if not modelli_disponibili:
    modelli_disponibili = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Inizializzazione della cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# STILE GRAFICO (CSS CUSTOM)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo chiaro pulito */
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
    }

    /* Sidebar scura e compatta */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    /* Header e Logo Centrale */
    .brand-hero {
        text-align: center;
        padding-top: 40px;
        padding-bottom: 20px;
    }
    
    .logo-svg {
        width: 64px;
        height: 64px;
        margin-bottom: 12px;
    }

    .brand-hero h1 {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #0f172a;
        margin: 0;
    }
    
    .brand-hero h1 span {
        color: #2563eb;
    }

    .brand-hero p {
        font-size: 15px;
        color: #64748b;
        margin-top: 8px;
        max-width: 580px;
        margin-left: auto;
        margin-right: auto;
    }

    /* RIMOZIONE BORDO ROSSO & RISTRUTTURAZIONE INPUT BAR */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        border-color: #e2e8f0 !important;
        border-radius: 24px !important;
    }

    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* Override specifico per stChatInput */
    .stChatInputContainer {
        border-radius: 28px !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04) !important;
    }

    .stChatInputContainer:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
    }

    /* Stile messaggi della chat */
    .stChatMessage {
        background-color: transparent !important;
        padding: 1rem 0 !important;
    }

    .status-badge {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DEFINIZIONE LOGO SVG (MigliorIA Icon)
# ---------------------------------------------------------
SVG_LOGO_BLUE = """
<svg class="logo-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" rx="22" fill="#2563EB"/>
    <path d="M25 72V40L50 24L75 40V72" stroke="white" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M40 72V52H60V72" stroke="white" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="50" cy="38" r="5" fill="#60A5FA"/>
    <path d="M78 22L82 28L88 32L82 36L78 42L74 36L68 32L74 28L78 22Z" fill="#F59E0B"/>
</svg>
"""

SVG_LOGO_SIDEBAR = """
<svg style="width:36px; height:36px; vertical-align:middle; margin-right:8px;" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" rx="22" fill="#2563EB"/>
    <path d="M25 72V40L50 24L75 40V72" stroke="white" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M40 72V52H60V72" stroke="white" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="50" cy="38" r="5" fill="#60A5FA"/>
    <path d="M78 22L82 28L88 32L82 36L78 42L74 36L68 32L74 28L78 22Z" fill="#F59E0B"/>
</svg>
"""

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"<div>{SVG_LOGO_SIDEBAR} <span style='font-size:22px; font-weight:800; color:white;'>Miglior<span style='color:#3b82f6;'>IA</span></span></div>", unsafe_allow_html=True)
    st.caption("AI Suite per Gare d'Appalto")
    st.markdown("---")

    menu = st.radio(
        "NAVIGAZIONE",
        [
            "📄 Analisi capitolato", 
            "🔍 Ricerca prodotto", 
            "🏆 Confronto miglioria", 
            "📚 CAM e documentazione"
        ]
    )

    st.markdown("---")
    st.markdown("<p style='color: #94a3b8; font-size: 12px; margin-bottom: 5px;'>MOTORE AI ATTIVO</p>", unsafe_allow_html=True)
    
    modello_selezionato = st.selectbox(
        "Seleziona modello:",
        options=modelli_disponibili,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🗑️ Nuova Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='status-badge'>🟢 Groq Cloud Connesso</span>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------------

# Mostra Header + Logo solo se non ci sono messaggi nella chat
if len(st.session_state.messages) == 0:
    st.markdown(f"""
    <div class="brand-hero">
        {SVG_LOGO_BLUE}
        <h1>Miglior<span>IA</span></h1>
        <p>Incolla una voce di capitolato per analizzare requisiti, vincoli normativi e proposte di miglioria.</p>
    </div>
    """, unsafe_allow_html=True)

# Visualizzazione dei messaggi inviati
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# BARRA CHAT IN BASSO (NO BORDI ROSSI)
# ---------------------------------------------------------
if prompt_input := st.chat_input("Incolla qui la voce di capitolato da analizzare..."):

    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    system_prompt = f"""
Sei un esperto senior di capitolati tecnici e gare d'appalto nel settore delle costruzioni ed ingegneria.

Analizza la seguente voce di capitolato:
{prompt_input}

Rispondi in modo chiaro e ben strutturato in Markdown:
### 🔍 Requisiti e Prestazioni Principali
### ⚠️ Criticità e Vincoli di Gara
### 💡 Proposte di Miglioria Tecnico-Economica (almeno 5 punti)
### 🌱 Conformità ai Criteri Ambientali Minimi (CAM)
"""

    with st.chat_message("assistant"):
        if not client:
            error_msg = "⚠️ API Key non trovata nei Secrets di Streamlit."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            with st.spinner(f"Analisi in corso con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": system_prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                    )
                    risposta = chat_completion.choices[0].message.content
                    st.markdown(risposta)
                    
                    st.session_state.messages.append({"role": "assistant", "content": risposta})

                except Exception as e:
                    error_msg = f"Errore durante l'elaborazione API: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})