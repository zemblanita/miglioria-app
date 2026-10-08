import streamlit as st
import json
from groq import Groq

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MigliorIA | Engineering AI Suite",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
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

# ---------------------------------------------------------
# STILE GRAFICO AVANZATO (CUSTOM CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Importazione font professionale Google Sans / Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo applicazione */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Sidebar Dark Premium */
    [data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Header e Titolo Brand */
    .brand-container {
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 25px;
    }
    .brand-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        margin: 0;
    }
    .brand-title span {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-badge {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        display: inline-block;
        margin-left: 8px;
    }
    .brand-subtitle {
        font-size: 15px;
        color: #94a3b8;
        margin-top: 6px;
    }

    /* Feature Cards con effetto Glassmorphism */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .glass-card h4 {
        color: #60a5fa;
        font-size: 16px;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 8px;
    }
    .glass-card p {
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.5;
        margin: 0;
    }

    /* Personalizzazione dell'Area di Testo */
    .stTextArea textarea {
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        font-size: 14px !important;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Status indicator */
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
    st.markdown("## 🏗️ **MigliorIA**")
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
    st.markdown("**⚙️ Motore AI Cloud**")
    
    modello_selezionato = st.selectbox(
        "Modello attivo:",
        options=modelli_disponibili,
        index=0
    )

    st.markdown("---")
    st.markdown('<span class="status-dot"></span><span style="color:#10b981; font-size:12px; font-weight:600;">Groq Cloud Connected</span>', unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER BRAND
# ---------------------------------------------------------
st.markdown("""
<div class="brand-container">
    <div class="brand-title">Miglior<span>IA</span> <span class="brand-badge">PRO SUITE</span></div>
    <div class="brand-subtitle">Piattaforma di Intelligenza Artificiale per l'ottimizzazione tecnica dei capitolati d'appalto.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN - ANALISI CAPITOLATO
# ---------------------------------------------------------
if menu == "📄 Analisi capitolato":

    with st.container():
        st.subheader("📋 Input Voce di Capitolato")
        
        voce = st.text_area(
            "Incolla qui il testo tecnico o il requisito di gara da analizzare:",
            height=200,
            placeholder='Esempio: "Fornitura e posa in opera di corpi illuminanti a LED per esterni con flusso luminoso non inferiore a 12.000 lm, indice di resa cromatica Ra>80, grado di protezione IP66 e resistenza agli urti IK08..."'
        )
        
        col_count, col_btn = st.columns([1, 2])
        with col_count:
            st.caption(f"Caratteri inseriti: {len(voce)} / 10.000")
        with col_btn:
            analizza_clicked = st.button("🚀 AVVIA ANALISI AI", type="primary", use_container_width=True)

    if analizza_clicked:
        if not client:
            st.error("⚠️ API Key di Groq non trovata nei Secrets di Streamlit.")
        elif voce.strip():
            prompt = f"""
Sei un esperto senior di capitolati tecnici e gare d'appalto nel settore delle costruzioni ed ingegneria.

Analizza la seguente voce di capitolato:
{voce}

Fornisci una risposta ben strutturata in Markdown con i seguenti punti:
### 1. 🔍 Requisiti e Prestazioni Chiave
### 2. ⚠️ Criticità e Vincoli Tecnici
### 3. 💡 5 Proposte di Miglioria Tecnico-Economica
Per ogni proposta specifica il **Vantaggio Tecnico**, l'**Impatto di Sostenibilità (CAM)** e la **Valutazione Economica**.
"""
            with st.spinner(f"Analisi ad alta precisione con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                    )
                    
                    risposta = chat_completion.choices[0].message.content

                    st.success("✨ Analisi completata con successo!")
                    
                    # Box Risultato
                    with st.container(border=True):
                        st.markdown(risposta)

                except Exception as e:
                    st.error(f"Errore durante l'elaborazione API: {e}")
        else:
            st.warning("Inserisci una voce di capitolato prima di procedere.")

    st.write("")
    st.write("")

    # Cards informative in basso
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="glass-card"><h4>⚡ Analisi Istantanea</h4><p>Estrazione automatica dei requisiti stringenti e dei vincoli normativi.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h4>🎯 Strategy Migliorie</h4><p>Punti chiave ad alto valore per massimizzare il punteggio tecnico in gara.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card"><h4>🌱 Conformità CAM</h4><p>Verifica immediata dell\'allineamento ai Criteri Ambientali Minimi.</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="glass-card"><h4>📊 Export Pronto</h4><p>Risultati già formattati per la redazione delle relazioni tecniche.</p></div>', unsafe_allow_html=True)

else:
    st.info(f"Sezione **{menu}** in fase di sviluppo.")

# Footer
st.markdown("---")
st.caption("MigliorIA Pro Suite | Powered by Groq Cloud Infrastructure")