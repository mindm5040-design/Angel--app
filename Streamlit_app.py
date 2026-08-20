import streamlit as st
import requests
import base64
import os
import re
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

# --- MOTEUR AUDIO + LECTURE VOCALE QUI MARCHE SUR MOBILE ---
components.html("""
<script>
const parentDoc = window.parent.document;

// Débloque l'audio au premier clic
let audioCtx = null;
function getCtx(){
  if(!audioCtx){
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

function playPop(){
  try{
    const ctx = getCtx();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine'; o.frequency.value = 800;
    o.connect(g); g.connect(ctx.destination);
    g.gain.setValueAtTime(0.8, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime+0.2);
    o.start(); o.stop(ctx.currentTime+0.2);
  }catch(e){}
}

function playDing(){
  try{
    const ctx = getCtx();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type='sine'; o.frequency.value=1200;
    o.connect(g); g.connect(ctx.destination);
    g.gain.setValueAtTime(0.6, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime+0.4);
    o.start(); o.stop(ctx.currentTime+0.4);
  }catch(e){}
}

function speakText(txt){
  if(!txt) return;
  window.speechSynthesis.cancel();
  const clean = txt.replace(/\\$\\$|\\$/g,'').replace(/[\\[\\]]/g,'').substring(0,1000);
  const u = new SpeechSynthesisUtterance(clean);
  u.lang = 'fr-FR'; u.rate = 1; u.volume = 1;
  window.speechSynthesis.speak(u);
}

// Ecoute envoi
parentDoc.addEventListener('click', function(e){
  const btn = e.target.closest('button[data-testid="stChatInputSubmitButton"]');
  if(btn){
    playPop();
    localStorage.setItem('angel_waiting','1');
  }
}, true);

// Ecoute messages
setInterval(function(){
  if(localStorage.getItem('angel_waiting')==='1'){
    const msgs = parentDoc.querySelectorAll('div[data-testid="stChatMessage"]');
    if(msgs.length>0 && msgs.length%2===0){
      playDing();
      localStorage.removeItem('angel_waiting');
      // Auto lecture vocale si activé
      if(localStorage.getItem('angel_tts_auto')==='1'){
        const last = msgs[msgs.length-1];
        speakText(last.innerText);
      }
    }
  }
}, 600);

// Fonction appelée par les boutons 🔊
window.angelSpeak = function(id){
  const el = parentDoc.getElementById(id);
  if(el){ speakText(el.innerText); }
}
window.angelStop = function(){ window.speechSynthesis.cancel(); }
</script>
<div style="display:none">Angel Audio Engine OK</div>
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
    if not text: return text
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
.tts-btn {background:#0a0a0a!important; color:white!important; border-radius:20px!important; padding:4px 12px!important; font-size:12px!important;}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    p = Path("brain.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="font-size:90px;">🧠</div>'

st.markdown(f'<div class="brain-container">{get_video_html()}<div class="angel-title">Angel AI</div></div>', unsafe_allow_html=True)

# Interrupteur lecture auto
auto_tts = st.toggle("🔊 Lecture vocale auto", value=False)
components.html(f"<script>localStorage.setItem('angel_tts_auto','{1 if auto_tts else 0}');</script>", height=0)

if not KEY:
    st.warning("Mets ta cle GROQ")
    st.stop()

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Premiere"

def ask_groq(q, img=None):
    try:
        system_prompt = "Tu es Angel prof. Maths avec $$ $$."
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

# Affichage messages avec bouton 🔊
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(f'<div id="msg-{i}">{fix_latex(m["content"])}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            components.html(f"""
            <button onclick="window.parent.angelSpeak('msg-{i}')" style="background:#0a0a0a;color:white;border:none;border-radius:20px;padding:6px 14px;font-size:12px;cursor:pointer;margin-top:6px">🔊 Lire vocalement</button>
            <button onclick="window.parent.angelStop()" style="background:#eee;color:#000;border:none;border-radius:20px;padding:6px 10px;font-size:12px;cursor:pointer;margin-left:6px">⏹️</button>
            """, height=40)

prompt = st.chat_input("Question niveau " + st.session_state.classe + "...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    rep = ask_groq(prompt)
    st.session_state.messages.append({"role": "assistant", "content": rep})
    st.rerun()
