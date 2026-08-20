import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
header, footer {visibility:hidden!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:20px!important;}

/* CACHE LES BOUTONS STREAMLIT POUR FAIRE DES RONDS BLEUS */
div[data-testid="column"] button {
    background:#0a2da6!important;
    color:white!important;
    border:none!important;
    border-radius:50%!important;
    width:38px!important; height:38px!important;
    font-size:20px!important; font-weight:bold!important;
    padding:0!important;
}
div[data-testid="column"] button:hover {background:#082080!important;}

/* LA BULLE MESSAGE COMME SUR TON IMAGE */
div[data-testid="stTextInput"] input {
    background:#f0f2f5!important;
    border:none!important;
    border-radius:20px!important;
    height:40px!important;
    padding-left:18px!important;
    font-size:15px!important;
    color:#65676b!important;
}
div[data-testid="stTextInput"] {width:100%!important;}

/* BOUTON ENVOI BLEU A DROITE */
div[data-testid="column"]:last-child button {
    background:#0a2da6!important;
    border-radius:50%!important;
}
</style>
""", unsafe_allow_html=True)

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
FILE = "angel_memory.json"

def load():
    if os.path.exists(FILE):
        try:
