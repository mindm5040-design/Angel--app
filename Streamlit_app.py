import streamlit as st
st.set_page_config(page_title="NEXA-AI", layout="wide")
st.markdown("<style>.stApp{background:#08080A;color:white;}header,footer,#MainMenu{visibility:hidden;}</style>", unsafe_allow_html=True)
st.markdown("# NEXA-AI 🧬")
st.markdown("### System recovering...")
st.success("App relancée avec succès !")
if st.button("Lancer NEXA-AI HIGH-TECH"):
    st.balloons()
    st.write("Maintenant colle le code high-tech que je t'ai donné")
