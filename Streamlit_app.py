
import streamlit as st
import requests
import base64
import os
import re
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

# --- SON QUI MARCHE ---
components.html("""
<audio id="send-sound" src="https://cdn.pixabay.com/download/audio/2022/03/24/audio_9bd4170e8d.mp3" preload="auto"></audio>
<audio id="receive-sound" src="https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c8a5b8.mp3" preload="auto"></audio>
<style> audio { display:none; } </style>
<script>
const parentDoc = window.parent.document;

function getAudio(id){
  return document.getElementById(id) || parentDoc.getElementById(id);
}

parentDoc.addEventListener('click', function(e){
  const btn = e.target.closest('button[data-testid="stChatInputSubmitButton"]');
  if(btn){
    const a = document.getElementById('send-sound');
    if(a){ a.currentTime=0; a.volume=0.8; a.play().catch(()=>{}); }
    window.parent.waitingForAngel = true;
    localStorage.setItem('angel_waiting','1');
  }
}, true);

setInterval(() => {
  if(localStorage.getItem('angel_waiting') === '1'){
    const msgs = parentDoc.querySelectorAll('div[data-testid="stChatMessage"]');
    const lastMsgs = window.parent.lastMsgCount || 0;
    if(msgs.length > lastMsgs && msgs.length % 2 === 0){
       const a = document.getElementById('receive-sound');
       if(a){ a.currentTime=0; a.volume=0.8; a.play().catch(()=>{}); }
       localStorage.removeItem('angel_waiting');
    }
    window.parent.lastMsgCount = msgs.length;
  }
}, 300);
</script>
""", height=0)

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except: pass
    return os.getenv("GROQ_API_KEY", "")

KEY = get_groq_key()

def fix_latex(text):
    if not text: return text
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    return text

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;600&display=swap');
.stApp {background:#FCFCF9!important; font-family:'DM Sans', sans-serif!important;}
header, footer, #MainMenu,.stDeployButton {visibility:hidden!important;}
.brain-container {display:flex; flex-direction:column; align-items:center; margin:10px 0 6px;}
.brain-video {width:140px; height:140px; border-radius:50%; object-fit:cover; box-shadow:0 0 40px rgba(224,122,79,0.3); border:2px solid #E07A4F;}
.angel-title {font-family:'Space Grotesk'; font-size:44px; font-weight:700; letter-spacing:-2px; text-align:center; margin-top:14px;}
div[data-testid="stButton"] > button {background: rgba(255,255,255,0.75)!important; backdrop-filter: blur(20px)!important; border:1px solid rgba(0,0,0,0.06)!important; border-radius:18px!important; height:72px!important; font-family:'Space Grotesk'!important; font-weight:600!important; color:#0a0a0a!important;}
button[kind="primary"] {background:#0a0a0a!important; color:white!important;}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    p = Path("brain.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="font-size:90px;">🧠</div>'

st.markdown(f"""
<div class="brain-container">
  {get_video_html()}
  <div class="angel-title">Angel AI</div>
  <div style="color:#E07A4F; font-size:10px; letter-spacing:3px; font-weight:700; text-align:center; margin-top:6px;">NEURAL ENGINE • ACTIVE</div>
</div>
""", unsafe_allow_html=True)

if not KEY:
    st.warning("⚠️ Mets ta clé dans Settings → Secrets")
    st.code('GROQ_API_KEY = "gsk_..."')
    st.stop()

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Master 1"

def ask_groq(q, img=None):
    try:
        system_prompt = f"""Tu es Angel, prof niveau {st.session_state.classe}.
REGLE MATHS: Écris TOUTES les formules avec $$ $$ et $ $. INTERDIT \\[ \\]."""
        if img:
            b64=base64.b64encode(img).decode()
            payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":f"{system_prompt}\n\n[{st.session_state.classe}] {q}"},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
        else:
            payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":system_prompt},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/open
