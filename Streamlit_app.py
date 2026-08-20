import streamlit as st
import requests, base64, os, re
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI — by Lelouch", page_icon="✦", layout="wide")

# --- AUDIO + TTS ---
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

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets: return st.secrets["GROQ_API_KEY"]
    except: pass
    return os.getenv("GROQ_API_KEY","")
KEY=get_key()

def fix_latex(t):
    if not t: return t
    t=t.replace("$$\\LaTeX$$","").replace("$$LaTeX$$","")
    t=re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', t, flags=re.DOTALL)
    t=re.sub(r'\\\((.*?)\\\)', r'$\1$', t, flags=re.DOTALL)
    return t

# --- STYLE CLAUDE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&display=swap');
.stApp {background:#FAF9F5!important;}
header, footer, #MainMenu,.stDeployButton {visibility:hidden!important;}
[data-testid="stSidebar"] {background:#F5F3EF!important; border-right:1px solid #E8E3DC!important;}
[data-testid="stSidebar"] * {font-family:'Inter', sans-serif!important;}
.claude-logo {font-family:'Instrument Serif', serif; font-size:26px; font-weight:400; letter-spacing:-0.5px; padding:16px 12px;}
.claude-newchat {background:#111111!important; color:white!important; border-radius:10px!important; height:44px!important; font-family:'Inter'!important; font-weight:500!important; width:100%; border:none!important; margin:8px 0;}
.claude-history-title {font-size:11px; letter-spacing:1.2px; color:#9A958E; font-weight:600; margin:24px 12px 8px; font-family:'Inter';}
.brain-wrap {display:flex; flex-direction:column; align-items:center; justify-content:center; padding:60px 0 20px;}
.brain-video {width:96px; height:96px; border-radius:24px; object-fit:cover; box-shadow:0 8px 32px rgba(0,0,0,0.08); border:1px solid #E8E3DC;}
.angel-title {font-family:'Instrument Serif', serif; font-size:52px; font-weight:400; letter-spacing:-1.5px; margin-top:20px; color:#111;}
.angel-sub {font-family:'Inter'; font-size:14px; color:#6B6560; margin-top:8px; letter-spacing:0.2px;}
.claude-input [data-testid="stChatInput"] {border:1px solid #E8E3DC!important; background:white!important; border-radius:24px!important; box-shadow:0 2px 16px rgba(0,0,0,0.04)!important;}
.claude-card {background:white; border:1px solid #E8E3DC; border-radius:16px; padding:16px; margin:8px 0; font-family:'Inter';}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    for p in [Path("brain.mp4"), Path(__file__).parent / "brain.mp4"]:
        if p.exists():
            b64=base64.b64encode(p.read_bytes()).decode()
            return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="width:96px;height:96px;background:#111;border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:40px;">✦</div>'

if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets"); st.stop()
if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Premiere"

def ask_groq(q, img=None):
    try:
        sys = f"Tu es Angel, IA pro niveau {st.session_state.classe}. Maths avec $ $ et $$ $$. Ne dis jamais LaTeX."
        url="https://api.groq.com/openai/v1/chat/completions"
        h={"Authorization":"Bearer "+KEY}
        if img:
            b64=base64.b64encode(img).decode()
            payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":sys+" "+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":sys},{"role":"user","content":q}]}
        r=requests.post(url,headers=h,json=payload,timeout=60).json()
        return fix_latex(r["choices"][0]["message"]["content"])
    except Exception as e: return f"Erreur: {e}"

# SIDEBAR STYLE CLAUDE
with st.sidebar:
    st.markdown('<div class="claude-logo">✦ Angel</div>', unsafe_allow_html=True)
    if st.button("＋ Nouveau chat", key="new", use_container_width=True):
        st.session_state.messages=[]; st.rerun()
    st.markdown('<div class="claude-history-title">NIVEAU</div>', unsafe_allow_html=True)
    for cat, items in [("Collège",["6e","5e","4e","3e"]),("Lycée",["Seconde","Premiere","Terminale"]),("Université",["Licence 1","Master 1","Master 2"])]:
        st.markdown(f'<div style="font-size:12px;font-weight:600;margin:12px 12px 6px;color:#111">{cat}</div>', unsafe_allow_html=True)
        for c in items:
            if st.button(c, key=f"cl_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c; st.rerun()
    st.markdown('<div class="claude-history-title">OUTILS</div>', unsafe_allow_html=True)
    up=st.file_uploader("📎 Importer devoir", type=["jpg","png","jpeg"], label_visibility="visible")
    if up and st.button("Analyser photo", type="primary", use_container_width=True):
        rep=ask_groq("Explique cet exercice étape par étape", up.getvalue())
        st.session_state.messages+=[{"role":"user","content":"📎 Photo"},{"role":"assistant","content":rep}]
        st.rerun()

# PAGE PRINCIPALE
if len(st.session_state.messages)==0:
    st.markdown(f"""
    <div class="brain-wrap">
        {get_video_html()}
        <div class="angel-title">Angel AI</div>
        <div class="angel-sub">Un assistant intelligent et bienveillant pour tes études — niveau {st.session_state.classe}</div>
        <div style="display:flex; gap:8px; margin-top:28px; flex-wrap:wrap; justify-content:center;">
            <div class="claude-card">📐 Explique ce théorème</div>
            <div class="claude-card">📸 Corrige mon exercice</div>
            <div class="claude-card">✍️ Rédige une dissertation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

for i,m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(f'<div id="msg-{i}">{fix_latex(m["content"])}</div>', unsafe_allow_html=True)
        if m["role"]=="assistant":
            components.html("<script>try{window.parent.playDing();}catch(e){}</script>", height=0)
            components.html(f"""
            <div style="margin-top:10px;display:flex;gap:6px">
              <button onclick="window.parent.angelSpeak('msg-{i}')" style="background:white;border:1px solid #E8E3DC;border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer">🔊 Écouter</button>
              <button onclick="window.parent.angelStop()" style="background:#F5F3EF;border:1px solid #E8E3DC;border-radius:20px;padding:6px 10px;font-size:12px;cursor:pointer">⏹️</button>
            </div>
            """, height=40)

st.markdown('<div class="claude-input">', unsafe_allow_html=True)
prompt=st.chat_input(f"Poser une question à Angel — {st.session_state.classe}...")
st.markdown('</div>', unsafe_allow_html=True)

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask_groq(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
