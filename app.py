with st.sidebar:
    # Header Logo + Titolo affiancati con colonne native
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