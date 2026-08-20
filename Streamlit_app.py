import streamlit as st
import requests
import base64
import os
import re
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

# SONS
components.html("""
<audio id="send-sound" src="https://cdn.pixabay.com/download/audio/2022/03/24/audio_9bd4170e8d.mp3" preload="auto"></audio>
<audio id="receive-sound" src="https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c8a5b8.mp3" preload="auto"></audio>
<script>
const parentDoc = window.parent.document;
parentDoc.addEventListener('click', function(e){
  const btn = e.target.closest('button[data-testid="stChatInputSubmitButton"]');
  if(btn){
    const a = document.getElementById('send-sound');
    if(a){ a.currentTime=0; a.volume=0.8; a.play(); }
    localStorage.setItem('angel_waiting','1');
  }
}, true);
setInterval(function(){
  if(localStorage.getItem('angel_waiting')==='1'){
    const msgs = parentDoc.querySelectorAll('div[data-testid="stChatMessage"]');
    if(msgs.length>0 && msgs.length%2===0){
       const a = document.getElementById('receive-sound');
       if(a){ a.currentTime=0; a.volume=0.8; a.play(); }
       localStorage.removeItem('angel_waiting');
    }
  }
}, 500);
</script>
""", height=0)

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")

KEY = get_groq_key()

def fix_latex(text):
    if not text:
        return text
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    return text

st.markdown("""
<style>
.stApp {background:#FCFCF9!important;}
header, footer, #MainMenu {visibility:hidden!important;}
.brain-container {display:flex; flex-direction:column; align-items:center; margin:10px 0 6px;}
.brain-video {width:140px; height:140px; border-radius:50%; object-fit:cover; border:2px solid #E07A4F;}
.angel-title {font-size:44px; font-weight:700; text-align:center; margin-top:14px;}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    p = Path("brain.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="font-size:90px;">🧠</div>'

st.markdown(f'<div class="brain-container">{get_video_html()}<div class="angel-title">Angel AI</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Mets ta cle GROQ dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "classe" not in st.session_state:
    st.session_state.classe="Premiere"

def ask_groq(q, img=None):
    try:
        system_prompt = "Tu es Angel prof. Ecris maths avec $$ $$ seulement."
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": "Bearer " + KEY}
        if img:
            b64 = base64.b64encode(img).decode()
            payload = {"model": "meta-llama/llama-4-scout-17b-16e-instruct", "messages": [{"role": "user", "content": [{"type": "text", "text": q}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
        else:
            payload = {"model": "openai/gpt-oss-20b", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": q}]}
        r = requests.post(url, headers=headers, json=payload, timeout=60).json()
        return fix_latex(r["choices"][0]["message"]["content"])
    except Exception as e:
        return f"Erreur: {e}"

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(fix_latex(m["content"]))

prompt = st.chat_input("Question niveau " + st.session_state.classe + "...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    rep = ask_groq(prompt)
    st.session_state.messages.append({"role": "assistant", "content": rep})
    st.rerun()
