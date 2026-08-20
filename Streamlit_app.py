import streamlit as st
import requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

# --- CSS QUI FORCE HORIZONTAL COMME TON IMAGE ---
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
header, footer {visibility:hidden!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:10px!important;}

/* FORCE LA BARRE EN HORIZONTAL MEME SUR MOBILE */
div[data-testid="stHorizontalBlock"]:has(button) {
    display:flex!important;
    flex-direction:row!important;
    flex-wrap:nowrap!important;
    align-items:center!important;
    gap:6px!important;
    max-width:720px; margin:0 auto;
    background:white;
    padding:8px 0;
    border-top:1px solid #e4e6eb;
}
div[data-testid="column"] {
    flex:0 0 auto!important;
    min-width:auto!important;
}
div[data-testid="column"]:nth-child(5) {
    flex:1 1 auto!important;
}

/* STYLE BOUTONS */
div[data-testid="column"] button {
    border-radius:12px!important;
    height:38px!important;
}
div[data-testid="column"]:nth-child(6) button {
    background:#ff2d2d!important;
    color:white!important;
    border-radius:10px!important;
}
div[data-testid="stTextInput"] input {
    background:#f0f2f5!important;
    border:none!important;
    border-radius:20px!important;
    height:40px!important;
}
</style>
""", unsafe_allow_html=True)

FILE = "angel_memory.json"
KEY = st.secrets.get("GROQ_API_KEY","").strip()

def load_chats():
    if not os.path.exists(FILE): return []
    try:
        with open(FILE,"r",encoding="utf-8") as f:
            d=json.load(f)
            if isinstance(d, dict): return []
            return [m for m in d if isinstance(m, dict) and m.get("role") in ["user","assistant"]]
    except: return []

def save_chats(chats):
    try:
        with open(FILE,"w",encoding="utf-8") as f:
            json.dump(chats,f,ensure_ascii=False,indent=2)
    except: pass

if "chats" not in st.session_state: st.session_state.chats=load_chats()
if "tool" not in st.session_state: st.session_state.tool=None
if "last_q" not in st.session_state: st.session_state.last_q=""

def ask_groq(q, img=None):
    try:
        if img:
            b64=base64.b64encode(img).decode()
            body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
        else:
            body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":"Tu es Angel, prof qui explique simple."},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization": f"Bearer {KEY}"},json=body,timeout=40).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e: return f"Erreur: {e}"

# --- CHAT ---
for m in st.session_state.chats:
    with st.chat_message(m.get("role","user")):
        st.markdown(m.get("content",""))

# --- OUTILS ---
if st.session_state.tool=="photo":
    with st.container(border=True):
        up=st.file_uploader("",type=["jpg","png"],label_visibility="collapsed")
        cam=st.camera_input("",label_visibility="collapsed")
        img=cam.getvalue() if cam else (up.getvalue() if up else None)
        if img and st.button("Analyser",type="primary",use_container_width=True):
            ans=ask_groq("Résous cet exercice",img)
            st.session_state.chats.extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
            save_chats(st.session_state.chats); st.session_state.tool=None; st.rerun()
        if st.button("Fermer",use_container_width=True): st.session_state.tool=None; st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        aud=st.audio_input("",label_visibility="collapsed")
        if aud:
            try:
                files={"file":("a.wav",aud.getvalue(),"audio/wav")}
                data={"model":"whisper-large-v3","language":"fr"}
