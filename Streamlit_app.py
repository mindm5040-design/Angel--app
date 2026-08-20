import streamlit as st
import requests, base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🕊️", layout="centered")

st.markdown("""
<style>
.stApp {background:#0b1020!important;}
header, footer, #MainMenu {visibility:hidden!important;}
h1,h2,h3,p,span,div {color:#e2e8f0!important;}

div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}
.stChatMessage {background:transparent!important; border:none!important;}
div[data-testid="stChatMessageContent"] {padding:0!important;}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{
    background:#0a27a6!important; color:white!important;
    border-radius:18px 18px 4px 18px!important; padding:12px 16px!important; max-width:80%; margin-left:auto;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"]{
    background:#1e293b!important; color:#f1f5f9!important; border:1px solid #334155!important;
    border-radius:18px 18px 18px 4px!important; padding:12px 16px!important; max-width:80%;
}

div[data-testid="stBottom"] > div {background:#0b1020!important; border-top:1px solid #1e293b!important;}
input, textarea {background:#1e293b!important; color:white!important; border-radius:20px!important; border:1px solid #334155!important;}

div[data-testid="stExpander"] {background:#111a33!important; border:1px solid #1e3a8a!important; border-radius:14px!important;}
div[data-testid="stExpander"] summary {color:#7dd3fc!important; font-weight:700!important;}

div[data-testid="stButton"] > button {background:#1e293b!important; color:white!important; border:1px solid #334155!important; border-radius:10px!important; font-weight:600!important;}
div[data-testid="stButton"] > button:hover {background:#0a27a6!important; color:white!important; border-color:#0a27a6!important;}
button[kind="primary"] {background:#0a27a6!important; color:white!important;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if not KEY:
    st.error("Mets GROQ_API_KEY dans Secrets")
    st.stop()

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "classe" not in st.session_state:
    st.session_state.classe = "Master 1"

def ask(question, image=None):
    if image:
        b64 = base64.b64encode(image).decode()
        payload = {"model": "meta-llama/llama-4-scout-17b-16e-instruct","messages": [{"role": "user","content": [{"type": "text","text": f"[{st.session_state.classe}] {question}"},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        payload = {"model": "openai/gpt-oss-20b","messages": [{"role": "system","content": f"Tu es Angel, prof pour niveau {st.session_state.classe}. Tu expliques simple et clair."},{"role": "user","content": question}]}
    res = requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization": f"Bearer {KEY}"},json=payload,timeout=60).json()
    return res["choices"][0]["message"]["content"]

# --- ANIMATION LOGICIEL QUI TOURNE - STYLE HIGH TECH ---
components.html("""
<div style="width:100%; height:200px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:radial-gradient(circle at center, #1e3a8a44 0%, #0b1020 70%); border-radius:18px; border:1px solid #1e3a8a; position:relative;">
<style>
.loader {position:relative; width:90px; height:90px;}
.ring {position:absolute; width:100%; height:100%; border-radius:50%; border:2px solid transparent;}
.r1 {border-top:2px solid #00e5ff; border-right:2px solid #00e5ff44; animation: spin 1.2s linear infinite;}
.r2 {width:70%; height:70%; left:15%; top:15%; border-bottom:2px solid #0a27a6; border-left:2px solid #0a27a644; animation: spinR 1s linear infinite;}
.r3 {width:40%; height:40%; left:30%; top:30%; border-top:2px solid #fff; animation: spin 0.8s linear infinite;}
.center {position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); font-size:28px; animation: pulse 1.5s ease-in-out infinite;}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
@keyframes spinR{0%{transform:rotate
