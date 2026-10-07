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
    initial_sidebar_state="expanded"
)

# 🔑 RECUPERO SICURO API KEY
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        pass

# Modelli stabili e sempre disponibili
MODELLI_TOP = [
    "llama-3.1-8b-instant",    # ⚡ Velocissimo e sempre disponibile
    "llama3-70b-8192",         # 🧠 Alternativa 70B stabile
    "mixtral-8x7b-32768"       # 📚 Alternativa Mixtral
]

# ---------------------------------------------------------
# STILE GRAFICO (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #0f172a; }
    [data-testid="stSidebar"] * { color: #f1f5f9; }
    
    .brand-title { font-size: 38px; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
    .brand-title span { color: #2563eb; }
    .brand-subtitle { font-size: 15px; color: #64748b; margin-bottom: 24px; }

    .info-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .info-card h4 { margin-top: 0; font-size: 15px; font-weight: 600; color: #1e293b; }
    .info-card p { font-size: 13px; color: #64748b; margin-bottom: 0; }
    .system-status { font-size: 12px; color: #10b981; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ Miglior**IA**")
    st.caption("AI per gare d'appalto")
    st.markdown("---")

    menu = st.radio(
        "MENU NAVIGAZIONE",
        [
            "📄 Analisi capitolato", 
            "🔍 Ricerca prodotto", 
            "🏆 Confronto miglioria", 
            "📚 CAM e documentazione"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**⚙️ Motore IA Selezionato**")
    
    modello_selezionato = st.selectbox(
        "Scegli il modello IA:",
        options=MODELLI_TOP,
        index=0,
        help="llama-3.1-8b-instant è il motore più rapido e affidabile."
    )

    st.markdown("---")
    st.caption("MigliorIA | Powered by Groq Cloud")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown('<div class="brand-title">Miglior<span>IA</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-subtitle">'
    'L\'intelligenza artificiale al servizio delle tue gare d\'appalto. Analizza, migliora, ottimizza.'
    '</div>', 
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if menu == "📄 Analisi capitolato":

    with st.container(border=True):
        st.subheader("Voce di capitolato")
        
        voce = st.text_area(
            "Incolla qui la voce di capitolato da analizzare.",
            height=200,
            placeholder='Esempio: "Fornitura e posa di unità di climatizzazione con caratteristiche..."'
        )
        
        col_count, col_btn = st.columns([1, 2])
        with col_count:
            st.caption(f"Caratteri: {len(voce)} / 10000")
        with col_btn:
            analizza_clicked = st.button("✨ ANALIZZA VOCE", type="primary", use_container_width=True)

    if analizza_clicked:
        if not client:
            st.error("⚠️ API Key di Groq non configurata nei Secrets di Streamlit.")
        elif voce.strip():
            prompt = f"""
Sei un esperto di capitolati tecnici e gare d'appalto nel settore delle costruzioni.

Analizza la seguente voce di capitolato:
{voce}

Individua:
1. Le caratteristiche tecniche principali.
2. I vincoli che una miglioria deve rispettare.
3. Le possibili criticità della soluzione prevista.
4. Almeno 5 possibili direzioni di miglioria.
5. Per ogni miglioria spiega il vantaggio tecnico.

NON inventare prodotti o caratteristiche specifiche di prodotti reali.
In questa fase limitati all'analisi tecnica e alle possibili strategie di miglioramento.
"""
            with st.spinner(f"Analisi in corso con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                    )
                    
                    risposta = chat_completion.choices[0].message.content

                    st.success("Analisi completata!")
                    
                    with st.container(border=True):
                        st.markdown("### 📊 Risultato dell'analisi")
                        st.markdown(risposta)

                except Exception as e:
                    st.error(f"Errore durante l'analisi con {modello_selezionato}: {e}")
        else:
            st.warning("Inserisci prima una voce di capitolato.")

    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="info-card"><h4>📄 Analisi intelligente</h4><p>Estrai i requisiti, i vincoli e le criticità della voce con l\'AI.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-card"><h4>💡 Migliorie su misura</h4><p>Proposte concrete per sostenibilità, prestazioni e rapporto qualità/prezzo.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="info-card"><h4>📦 Prodotti e soluzioni</h4><p>Scopri soluzioni tecniche compatibili con i requisiti di gara e i CAM.</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="info-card"><h4>⭐ Confronta e scegli</h4><p>Metti a confronto le opzioni per individuare la soluzione vincente.</p></div>', unsafe_allow_html=True)

else:
    st.info(f"Sezione **{menu}** in fase di sviluppo.")

st.markdown("---")
footer_col1, footer_col2 = st.columns([4, 1])
with footer_col1:
    st.caption("MigliorIA | AI per gare d'appalto")
with footer_col2:
    st.markdown('<span class="system-status">🟢 Sistema attivo (Cloud API)</span>', unsafe_allow_html=True)