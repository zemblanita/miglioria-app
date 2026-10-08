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
    initial_sidebar_state="collapsed"  # Sidebar chiusa di default stile Gemini
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

# Inizializzazione della cronologia chat in sessione
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# STILE GRAFICO MINIMAL CHAT (GEMINI STYLE)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo chiaro e pulito */
    .stApp {
        background-color: #ffffff;
        color: #1f2937;
    }

    /* Sidebar scura e compatta */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    /* Titolo centrale stile Gemini */
    .chat-header {
        text-align: center;
        padding-top: 30px;
        padding-bottom: 20px;
    }
    .chat-header h1 {
        font-size: 36px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .chat-header h1 span {
        color: #2563eb;
    }
    .chat-header p {
        font-size: 15px;
        color: #6b7280;
        margin-top: 6px;
    }

    /* Stile messaggi della chat */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }

    /* Input bar fissa in basso stile Gemini */
    .stChatInput {
        border-radius: 28px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
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
# SIDEBAR (DI DEFAULT CHIUSA)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🏗️ Miglior<span style='color: #3b82f6;'>IA</span></h2>", unsafe_allow_html=True)
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
# MAIN LAYOUT (GEMINI CHAT STYLE)
# ---------------------------------------------------------

# Mostra l'header solo se la chat è vuota
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="chat-header">
        <h1>Miglior<span>IA</span></h1>
        <p>Incolla una voce di capitolato per analizzare vincoli, criticità e proposte di miglioria.</p>
    </div>
    """, unsafe_allow_html=True)

# Visualizzazione della cronologia dei messaggi nella chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# INPUT BAR FISSA IN BASSO AL CENTRO
# ---------------------------------------------------------
if prompt_input := st.chat_input("Incolla qui la voce di capitolato da analizzare..."):

    # 1. Mostra il messaggio dell'utente nella chat
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # 2. Prepara il prompt di analisi per l'AI
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

    # 3. Genera la risposta dell'AI sopra la barra di input
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
                    
                    # Salva la risposta nella sessione
                    st.session_state.messages.append({"role": "assistant", "content": risposta})

                except Exception as e:
                    error_msg = f"Errore durante l'elaborazione API: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})