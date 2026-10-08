import streamlit as st
from groq import Groq

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MigliorIA - Gare d'Appalto",
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
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("🏗️ MigliorIA")
    st.caption("AI Suite per Gare d'Appalto")
    st.divider()

    menu = st.radio(
        "Menu principale",
        [
            "📄 Analisi capitolato", 
            "🔍 Ricerca prodotto", 
            "🏆 Confronto miglioria", 
            "📚 CAM e documentazione"
        ]
    )

    st.divider()
    st.markdown("**Configurazione Engine**")
    
    modello_selezionato = st.selectbox(
        "Modello Groq attivo:",
        options=modelli_disponibili,
        index=0
    )

    st.divider()
    st.caption("🟢 Connesso a Groq Cloud API")

# ---------------------------------------------------------
# HEADER NATIVO E PULITO
# ---------------------------------------------------------
st.title("🏗️ MigliorIA")
st.subtitle = st.caption("Analisi intelligente dei capitolati tecnici e proposte di miglioria per gare d'appalto.")

st.divider()

# ---------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------
if menu == "📄 Analisi capitolato":

    st.subheader("Voce di Capitolato da Analizzare")
    
    # Text area pulita native Streamlit
    voce = st.text_area(
        label="Incolla il testo del capitolato o la specifica tecnica:",
        height=220,
        placeholder="Es: Fornitura e posa in opera di serramenti in alluminio a taglio termico con trasmittanza termica Uw non superiore a 1.3 W/m²K, abbattimento acustico 42 dB..."
    )

    col_info, col_btn = st.columns([2, 1])
    with col_info:
        st.caption(f"Caratteri inseriti: {len(voce)} / 10.000")
    with col_btn:
        analizza_clicked = st.button("✨ Avvia Analisi AI", type="primary", use_container_width=True)

    if analizza_clicked:
        if not client:
            st.error("⚠️ API Key non trovata nei Secrets di Streamlit.")
        elif voce.strip():
            prompt = f"""
Sei un esperto senior di capitolati tecnici e gare d'appalto nel settore delle costruzioni ed ingegneria.

Analizza la seguente voce di capitolato:
{voce}

Fornisci una risposta dettagliata e ben strutturata in Markdown:
### 1. 🔍 Requisiti e Prestazioni Chiave
Estrai le specifiche tecniche vincolanti e i parametri prestazionali richiesti.

### 2. ⚠️ Criticità e Vincoli di Gara
Evidenzia eventuali punti deboli, rischi di non conformità o ambiguità.

### 3. 💡 Proposte di Miglioria Tecnico-Economica
Proponi almeno 5 soluzioni tecniche per migliorare il punteggio in gara (es. prestazioni, sostenibilità, durabilità, manutenibilità).

### 4. 🌱 Conformità Criteri Ambientali Minimi (CAM)
Indica i requisiti CAM applicabili a questa tipologia di lavorazione/fornitura.
"""
            with st.spinner(f"Elaborazione in corso con {modello_selezionato}..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=modello_selezionato,
                        temperature=0.2,
                    )
                    risposta = chat_completion.choices[0].message.content

                    st.success("Analisi completata!")
                    
                    st.markdown("---")
                    st.markdown("### 📊 Risultato dell'Analisi")
                    st.markdown(risposta)

                except Exception as e:
                    st.error(f"Errore durante l'elaborazione API: {e}")
        else:
            st.warning("Inserisci una voce di capitolato per avviare l'analisi.")

else:
    st.info(f"Sezione **{menu}** in fase di sviluppo.")

st.divider()
st.caption("MigliorIA | Software di supporto tecnico per gare d'appalto")