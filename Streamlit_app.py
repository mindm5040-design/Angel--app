import streamlit as st
import requests
import base64
import os
import re
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI — by Lelouch", page_icon="✦", layout="wide")

# --- MOTEUR AUDIO + TTS ---
components.html("""
<script>
const pDoc=window.parent.document; const pWin=window.parent;
if(!pWin.angelAudioCtx){
 pWin.angelAudioCtx=null;
 pWin.getAngelCtx=function(){ if(!pWin.angelAudioCtx){pWin.angelAudioCtx=new(pWin.AudioContext||pWin.webkitAudioContext)();} return pWin.angelAudioCtx;}
 pWin.playPop=function(){ try{const ctx=pWin.getAngelCtx();const o=ctx.createOscillator();const g=ctx.createGain();o.frequency.value=800;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(0.8,ctx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,ctx.currentTime+0.2);o.start();o.stop(ctx.currentTime+0.2);}catch(e){}}
 pWin.playDing=function(){ try{const ctx=pWin.getAngelCtx();const o=ctx.createOscillator();const g=ctx.createGain();o.frequency.value=1200;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(0.6,ctx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,ctx.currentTime+0.5);o.start();o.stop(ctx.currentTime+0.5);}catch(e){}}
 pWin.angelSpeak=function(id){ try{pWin.speechSynthesis.cancel();const el=pDoc.getElementById(id);if(!el)return;let txt=el.innerText.replace(/\\$\\$/g,' ').replace(/\\$/g,' ');if(txt.length>800)txt=txt.substring(0,800);const u=new SpeechSynthesisUtterance(txt);u.lang='fr-FR';u.rate=0.95;pWin.speechSynthesis.speak(u);}catch(e){}}
 pWin.angelStop=function(){try{pWin.speechSynthesis.cancel();}catch(e){}}
 pDoc.addEventListener('click',function(e){const b=e.target.closest('button[data-testid="stChatInputSubmitButton"]');if(b)pWin.playPop();},true);
}
</script>
""", height=0)

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets: return st.secrets["GROQ_API_KEY"]
    except: pass
    return os.getenv("GROQ_API_KEY","")
KEY=get_groq_key()

def fix_latex(text):
    if not text: return text
    text=text.replace("$$\\LaTeX$$","").replace("$$LaTeX$$","").replace("$\\LaTeX$","")
    text=re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text=re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    return text

# --- STYLE PRO CLAUDE + ORIGINAL ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;600&family=Instrument+Serif&display=swap');
.stApp {background:#FCFCF9!important; font-family:'DM Sans', sans-serif!important;}
header, footer, #MainMenu,.stDeployButton {visibility:hidden!important;}
[data-testid="stSidebar"] {background:#F5F3EF!important; border-right:1px solid #E8E3DC!important;}
.brain-container {display:flex; flex-direction:column; align-items:center; margin:20px 0 6px;}
.brain-video {width:140px; height:140px; border-radius:50%; object-fit:cover; box-shadow:0 0 40px rgba(224,122,79,0.25); border:2px solid #E07A4F;}
.angel-title {font-family:'Space Grotesk'; font-size:44px; font-weight:700; letter-spacing:-2px; text-align:center; margin-top:14px;}
.neural {color:#E07A4F; font-size:10px; letter-spacing:3px; font-weight:700; text-align:center; margin-top:6px;}
div[data-testid="stButton"] > button {background: rgba(255,255,255,0.75)!important; backdrop-filter: blur(20px)!important; border:1px solid rgba(0,0,0,0.06)!important; border-radius:18px!important; height:58px!important; font-family:'Space Grotesk'!important; font-weight:600!important; color:#0a0a0a!important;}
button[kind="primary"] {background:#0a0a0a!important; color:white!important; border-radius:12px!important;}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    for p in [Path("brain.mp4"), Path("app/brain.mp4"), Path(__file__).parent / "brain.mp4"]:
        if p.exists():
            b64=base64.b64encode(p.read_bytes()).decode()
            return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="font-size:90px;">🧠</div>'

st.markdown(f"""
<div class="brain-container">
  {get_video_html()}
  <div class="angel-title">Angel AI</div>
  <div class="neural">NEURAL ENGINE • ACTIVE</div>
</div>
""", unsafe_allow_html=True)

if not KEY:
    st.warning("⚠️ Mets ta clé dans Settings → Secrets"); st.stop()

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Premiere"

def ask_groq(q, img=None):
    try:
        system_prompt=f"Tu es Angel, prof bienveillant niveau {st.session_state.classe}. Tu expliques clair étape par étape. Maths: $x^2$ et $$\\frac{{a}}{{b}}$$. Ne dis jamais le mot LaTeX."
        url="https://api.groq.com/openai/v1/chat/completions"
        headers={"Authorization":"Bearer "+KEY}
        if img:
            b64=base64.b64encode(img).decode()
            payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":system_prompt+"\n\nQuestion: "+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":system_prompt},{"role":"user","content":q}]}
        r=requests.post(url,headers=headers,json=payload,timeout=60).json()
        return fix_latex(r["choices"][0]["message"]["content"])
    except Exception as e:
        return f"Erreur: {e}"

# --- SELECTEUR CLASSE ORIGINAL ---
with st.expander(f"📚 Niveau: {st.session_state.classe}", expanded=False):
    for label, items in [("COLLEGE",["6e","5e","4e","3e"]),("LYCEE",["Seconde","Premiere","Terminale"]),("UNIVERSITE",["Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"])]:
        st.markdown(f'<div style="font-size:10px; letter-spacing:2px; color:#999; font-weight:700; margin:10px 0 6px;">{label}</div>', unsafe_allow_html=True)
        cols=st.columns(3)
        for i,c in enumerate(items):
            with cols[i%3]:
                if st.button(c, key=f"cl_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                    st.session_state.classe=c; st.rerun()

# --- MESSAGES + SONS + TTS ---
for i,m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(f'<div id="msg-{i}">{fix_latex(m["content"])}</div>', unsafe_allow_html=True)
        if m["role"]=="assistant":
            components.html("<script>try{window.parent.playDing();}catch(e){}</script>", height=0)
            components.html(f"""
            <div style="margin-top:8px">
              <button onclick="window.parent.angelSpeak('msg-{i}')" style="background:#0a0a0a;color:white;border:none;border-radius:20px;padding:7px 14px;font-size:12px;cursor:pointer">🔊 Lire vocalement</button>
              <button onclick="window.parent.angelStop()" style="background:#eee;color:#000;border:none;border-radius:20px;padding:7px 10px;font-size:12px;margin-left:6px;cursor:pointer">⏹️</button>
            </div>
            """, height=45)

# --- IMPORT PHOTO ORIGINAL RESTAURE ---
with st.expander("📸 Photo devoir + Caméra", expanded=False):
    up=st.file_uploader("Importer une photo", type=["jpg","png","jpeg"], label_visibility="visible")
    cam=st.camera_input("Prendre une photo", label_visibility="visible")
    img_bytes=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img_bytes and st.button("🔍 Analyser le devoir", type="primary", use_container_width=True):
        rep=ask_groq("Explique cet exercice étape par étape avec détails", img_bytes)
        st.session_state.messages+=[{"role":"user","content":"📸 Photo du devoir"},{"role":"assistant","content":rep}]
        st.rerun()

# --- CHAT INPUT ---
prompt=st.chat_input(f"Question niveau {st.session_state.classe}... (ex: explique pythagore)")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask_groq(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
