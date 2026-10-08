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

# ---------------------------------------------------------
# CSS PER REPLICARE IL MOCK-UP CON SCARITTE BIANCHE E LOGO MINIMAL
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Fondo chiaro generale */
    .stApp {
        background-color: #f3f4f6;
        color: #111827;
    }

    /* SIDEBAR SCURA CON TESTO BIANCO AD ALTO CONTRASTO */
    [data-testid="stSidebar"] {
        background-color: #0b1329 !important;
        padding-top: 24px;
    }
    
    /* Tutti gli elementi di testo della sidebar in BIANCO */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 10px !important;
        color: #ffffff !important;
    }

    /* Logo Minimal "M" Blu */
    .brand-logo-m {
        background-color: #2563eb;
        color: #ffffff !important;
        width: 36px;
        height: 36px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 20px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        letter-spacing: -0.5px;
    }

    /* HEADER */
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

    /* CARD PRINCIPALE INPUT */
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

    /* Text Area */
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

    /* Pulsante Blu */
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

    /* CARDS IN BASSO */
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
        color: #9ca3af