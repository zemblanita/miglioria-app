import streamlit as st
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
            if not any(banned in m.lower() for banned in ["whisper", "guard", "orpheus", "safetensors", "preview"])
        ]
        modelli_disponibili.sort(key=lambda x: ("llama" in x.lower(), x), reverse=True)
    except Exception:
        pass

if not modelli_disponibili:
    modelli_disponibili = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Inizializzazione cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# STILE CSS PER RIMUOVERE BORDI ROSSI
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Sfondo pulito */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Rimuove i bordi rossi sul focus dell'input bar */
    .stChatInputContainer {
        border: 1px solid #cbd5e1 !important;
        border-radius: 24px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    .stChatInputContainer:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("🏗️ MigliorIA")
    st.caption("AI Suite per Gare d'Appalto")
    st.divider()

    menu = st.radio(
        "Navigazione",
        [
            "📄 Analisi capitolato", 
            "🔍 Ricerca prodotto", 
            "🏆 Confronto miglioria", 
            "📚 CAM e documentazione"
        ]
    )

    st.divider()
    st.markdown("**Engine AI**")
    
    modello_selezionato = st.selectbox(
        "Modello attivo:",
        options=modelli_disponibili,
        index=0
    )

    st.divider()
    if st.button("🗑️ Nuova Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# MAIN INTERFACE (STILE GEMINI)
# ---------------------------------------------------------

# Mostra il titolo al centro solo se non ci sono ancora messaggi
if len(st.session_state.messages) == 0:
    st.markdown("<h1 style='text-align: center; margin-top: 50px; color: #0f172a;'>🏗️ MigliorIA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 16px;'>Incolla una voce di capitolato per avviare l'analisi intelligente.</p>", unsafe_allow_html=True)

# Stampa la cronologia dei messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# BARRA CHAT IN BASSO
# ---------------------------------------------------------
if prompt_input := st.chat_input("Incolla qui la voce di capitolato da analizzare..."):

    # Mostra messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Prompt di analisi
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

    # Risposta AI
    with st.chat_message("assistant"):
        if not client:
            st.error("⚠️ API Key di Groq non trovata nei Secrets di Streamlit.")
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
                    st.error(f"Errore durante l'elaborazione API: {e}")