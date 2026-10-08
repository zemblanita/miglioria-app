import streamlit as st
import urllib.parse
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
        
        # Filtriamo escludendo modelli non pertinenti o con limiti OTPM stringenti
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

# Inizializzazione cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# STILE CSS INTERFACCIA BLU E INPUT
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo applicazione in SFUMATURA BLU */
    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #0f172a 50%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Sidebar scura bluastra */
    [data-testid="stSidebar"] {
        background-color: #070a12 !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Titolo centrale e testo blu */
    .hero-title {
        text-align: center;
        margin-top: 40px;
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
    }
    .hero-title span {
        color: #3b82f6;
    }
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* Personalizzazione messaggi chat */
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        margin-bottom: 12px !important;
    }

    /* Input Bar in Basso - Stile Blu Tech (Niente bordi rossi) */
    .stChatInputContainer {
        border: 1px solid #334155 !important;
        border-radius: 28px !important;
        background-color: #0f172a !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    .stChatInputContainer:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
    }

    .stChatInput textarea {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🏗️ Miglior<span style='color: #3b82f6;'>IA</span></h2>", unsafe_allow_html=True)
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
# MAIN INTERFACE (CHAT BLU STYLE)
# ---------------------------------------------------------

# Mostra il titolo solo se la chat è vuota
if len(st.session_state.messages) == 0:
    st.markdown("<div class='hero-title'>🏗️ Miglior<span>IA</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Scrivi o incolla un materiale o voce di capitolato per identificare subito la miglioria e i link ai prodotti.</div>", unsafe_allow_html=True)

# Stampa la cronologia dei messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# BARRA CHAT IN BASSO
# ---------------------------------------------------------
if prompt_input := st.chat_input("Incolla qui un materiale o una voce di capitolato..."):

    # Mostra messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Prompt ottimizzato per estrarre migliorie E Generare Link ricerca prodotti
    system_prompt = f"""
Sei un esperto senior di capitolati tecnici, materiali da costruzione e gare d'appalto.

Analizza questo materiale / voce di capitolato:
"{prompt_input}"

Fornisci una risposta immediata, chiara e ben formattata in Markdown strutturata così:

### 💡 Miglioria Tecnica Consigliata
Spiega la miglioria principale da proporre in gara (prestazioni, sostenibilità, durabilità o risparmio).

### 🔍 Requisiti e Scheda Tecnica Chiave
Elenca in un elenco puntato i parametri fondamentali da verificare per il nuovo prodotto.

### 📦 Prodotti e Soluzioni Tecniche Suggerite
Proponi 3 marche/prodotti o tipologie di prodotti reali idonei.
Per OGNI prodotto o tipologia proposta, fornisci UN LINK DI RICERCA GOOGLE formattato in Markdown per accedere subito ai cataloghi o schede tecniche.

Esempio di formattazione link:
- **[Nome Prodotto / Produttore]**: [🔍 Cerca Schede Tecniche e Cataloghi](https://www.google.com/search?q=NOME_PRODOTTO+scheda+tecnica)

### 🌱 Note di Conformità CAM
Breve cenno sui Criteri Ambientali Minimi pertinenti per questa miglioria.
"""

    # Risposta AI
    with st.chat_message("assistant"):
        if not client:
            st.error("⚠️ API Key di Groq non trovata nei Secrets di Streamlit.")
        else:
            with st.spinner(f"Analisi e ricerca soluzioni in corso con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": system_prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                        max_tokens=1000
                    )
                    risposta = chat_completion.choices[0].message.content
                    st.markdown(risposta)
                    st.session_state.messages.append({"role": "assistant", "content": risposta})

                except Exception as e:
                    st.error(f"Errore durante l'elaborazione API: {e}")