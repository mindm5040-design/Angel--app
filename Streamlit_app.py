import streamlit as st
import requests
import base64
import os
import re
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

# MOTEUR AUDIO + TTS GLOBAL
components.html("""
<script>
// On installe tout dans le parent pour que les boutons puissent parler
const pDoc = window.parent.document;
const pWin = window.parent;

if(!pWin.angelAudioCtx){
  pWin.angelAudioCtx = null;
  pWin.getAngelCtx = function(){
    if(!pWin.angelAudioCtx){
      pWin.angelAudioCtx = new (pWin.AudioContext || pWin.webkitAudioContext)();
    }
    return pWin.angelAudioCtx;
  }
  pWin.playPop = function(){
    try{
      const ctx = pWin.getAngelCtx();
      const o = ctx.createOscillator(); const g = ctx.createGain();
      o.frequency.value=800; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.8, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime+0.2);
      o.start(); o.stop(ctx.currentTime+0.2);
    }catch(e){}
  }
  pWin.playDing = function(){
    try{
      const ctx = pWin.getAngelCtx();
      const o = ctx.createOscillator(); const g = ctx.createGain();
      o.frequency.value=1200; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.6, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime+0.5);
      o.start(); o.stop(ctx.currentTime+0.5);
    }catch(e){}
  }
  pWin.angelSpeak = function(id){
    try{
      pWin.speechSynthesis.cancel();
      const el = pDoc.getElementById(id);
      if(!el) return;
      let txt = el.innerText;
      txt = txt.replace(/\\$\\$/g,' ').replace(/\\$/g,' ').replace(/\\\\/g,' ');
      if(txt.length>800) txt = txt.substring(0,800);
      const u = new SpeechSynthesisUtterance(txt);
      u.lang='fr-FR'; u.rate=0.95;
      pWin.speechSynthesis.speak(u);
    }catch(e){}
  }
  pWin.angelStop = function(){ try{pWin.speechSynthesis.cancel();}catch(e){} }

  // Son envoi au clic
  pDoc.addEventListener('click', function(e){
    const btn = e.target.closest('button[data-testid="stChatInputSubmitButton"]');
    if(btn){ pWin.playPop(); }
  }, true);
}
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
    # Enleve le mot LaTeX écrit par l'IA
    text = text.replace("$$\\LaTeX$$", "").replace("$$LaTeX$$", "").replace("$\\LaTeX$", "")
    text = text.replace("en utilisant $$ $$", "").replace("en utilisant $$\\LaTeX$$", "")
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
    st.warning("Mets ta cle"); st.stop()

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Premiere"

def ask_groq(q, img=None):
    try:
        # PROMPT FIXE - plus jamais $$LaTeX$$
        system_prompt = f"""Tu es Angel, prof de maths niveau {st.session_state.classe}.
REGLES:
- Ecris les formules comme ca: $x^2$ ou $$\\frac{{1}}{{2}}$$
- Ne dis JAMAIS le mot LaTeX, n'ecris pas $$\\LaTeX$$, ecris directement la formule
- Parle en francais simple, sans dire que tu utilises LaTeX"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": "Bearer " + KEY}
        if img:
            b64 = base64.b64encode(img).decode()
            payload = {"model": "meta-llama/llama-4-scout-17b-16e-instruct", "messages": [{"role": "user", "content": [{"type": "text", "text": system_prompt + " Question: " + q}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
        else:
            payload = {"model": "openai/gpt-oss-20b", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": q}]}
        r = requests.post(url, headers=headers, json=payload, timeout=60).json()
        return fix_latex(r["choices"][0]["message"]["content"])
    except Exception as e:
        return f"Erreur: {e}"

for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(f'<div id="msg-{i}">{fix_latex(m["content"])}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            # DING reception
            components.html("<script>try{window.parent.playDing();}catch(e){}</script>", height=0)
            # BOUTONS qui appellent le parent
            components.html(f"""
            <div style="margin-top:8px">
              <button onclick="window.parent.angelSpeak('msg-{i}')" style="background:#0a0a0a;color:white;border:none;border-radius:20px;padding:7px 14px;font-size:12px;cursor:pointer">🔊 Lire vocalement</button>
              <button onclick="window.parent.angelStop()" style="background:#eee;color:#000;border:none;border-radius:20px;padding:7px 10px;font-size:12px;cursor:pointer;margin-left:6px">⏹️ Stop</button>
            </div>
            """, height=45)

prompt = st.chat_input("Question niveau " + st.session_state.classe + "...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    rep = ask_groq(prompt)
    st.session_state.messages.append({"role": "assistant", "content": rep})
    st.rerun()
