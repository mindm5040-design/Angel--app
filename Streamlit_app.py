import streamlit as st, requests, base64, time, re, json, uuid

st.set_page_config(page_title="LYRA", page_icon="✨", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');
* {font-family:'Inter', sans-serif;}
.stApp {background:#0f0f10; color:#ececec;}
section[data-testid="stSidebar"] {background:#18181b; border-right:1px solid #27272a;}
div[data-testid="stChatMessages"] {gap: 1.6rem!important; padding-top: 2rem; padding-bottom: 4rem;}
.stChatMessage {
    background:#18181b!important;
    border:1px solid #27272a!important;
    border-radius:20px!important;
    padding: 24px 28px!important;
    max-width: 820px!important;
    margin: 0 auto!important;
}
.stChatMessage p,.stChatMessage li {
    font-family:'Source Serif 4', serif!important;
    font-size: var(--lyra-font-size, 17px)!important;
    line-height: 1.85!important;
    letter-spacing: 0.2px!important;
    color: #f4f4f5!important;
}
.stChatMessage h1,.stChatMessage h2,.stChatMessage h3 {
    font-family:'Inter', sans-serif!important;
    font-weight:600!important;
    color:#fff!important;
    margin-top: 1.2em!important;
}
div[data-testid="stChatInput"] {
    background:#18181b!important;
    border:1px solid #3f3f46!important;
    border-radius:24px!important;
    max-width: 820px!important;
    margin: 0 auto!important;
}
.lyra-warning {
    background:#2a1f0f; border:1px solid #92620a; border-radius:12px;
    padding:12px 16px; color:#facc82; font-size:14px; margin-bottom:1rem;
}
.lyra-crisis {
    background:#2a0f0f; border:1px solid #b91c1c; border-radius:12px;
    padding:14px 18px; color:#fecaca; font-size:14px; margin-bottom:1rem; line-height:1.6;
}
.lyra-footer {
    text-align:center; color:#71717a; font-size:12px; padding:1.5rem 0 0.5rem 0;
}
.conv-btn button {
    text-align:left!important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
</style>
""", unsafe_allow_html=True)

if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {first_id: {"title": "Nouvelle conversation", "messages": []}}
    st.session_state.current_conv = first_id
if "niveau" not in st.session_state: st.session_state.niveau = "Terminale"
if "cycle" not in st.session_state: st.session_state.cycle = "Lycée"
if "last_call" not in st.session_state: st.session_state.last_call = 0.0
if "font_size" not in st.session_state: st.session_state.font_size = "Normale"

def current_messages():
    return st.session_state.conversations[st.session_state.current_conv]["messages"]

def set_conv_title_from_first_message(text):
    conv = st.session_state.conversations[st.session_state.current_conv]
    if conv["title"] == "Nouvelle conversation":
        conv["title"] = (text[:40] + "…") if len(text) > 40 else text

KEY = st.secrets.get("GROQ_API_KEY", "").strip()
CYCLES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
}
PROGRAMMES = {
    "6e": "bases fractions, décimaux, géométrie simple", "5e": "fractions, proportionnalité", "4e": "Pythagore, Thalès, équations",
    "3e": "fonctions, racine carrée, Brevet", "Seconde": "fonctions, vecteurs", "Première": "dérivées, suites",
    "Terminale": "limites, intégrales, Bac", "Licence 1": "analyse réelle, algèbre linéaire", "Licence 2": "analyse avancée",
    "Licence 3": "topologie", "Master 1": "master recherche", "Master 2": "expert", "Doctorat": "recherche doctorale"
}
MINEUR_CYCLES = {"Collège", "Lycée"}

CRISIS_PATTERNS = [r"\bsuicid", r"\bme tuer\b", r"\bme faire du mal\b", r"\benvie de mourir\b", r"\bscarification", r"\bplus envie de vivre\b",
