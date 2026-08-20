import streamlit as st
import requests, base64, os, re
from pathlib import Path
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="wide")

# --- AUDIO ---
components.html("""
<script>
const pDoc=window.parent.document; const pWin=window.parent;
if(!pWin.angelAudioCtx){
 pWin.angelAudioCtx=null;
 pWin.getAngelCtx=function(){ if(!pWin.angelAudioCtx){pWin.angelAudioCtx=new(pWin.AudioContext||pWin.webkitAudioContext)();} return pWin.angelAudioCtx;}
 pWin.playPop=function(){ try{const ctx=pWin.getAngelCtx();const o=ctx.createOscillator();const g=ctx.createGain();o.frequency.value=800;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(0.8,ctx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,ctx.currentTime+0.2);o.start();o.stop(ctx.currentTime+0.2);}catch(e){}}
 pWin.playDing=function(){ try{const ctx=pWin.getAngelCtx();const o=ctx.createOscillator();const g=ctx.createGain();o.frequency.value=1200;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(0.6,ctx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,ctx.currentTime+0.5);o.start();o.stop(ctx.currentTime+0.5);}catch(e){}}
 pWin.angelSpeak=function(id, lang){ try{pWin.speechSynthesis.cancel();const el=pDoc.getElementById(id);if(!el)return;let txt=el.innerText.replace(/\\$\\$/g,' ');if(txt.length>600)txt=txt.substring(0,600);const u=new SpeechSynthesisUtterance(txt);u.lang=lang||'fr-FR';u.rate=0.95;pWin.speechSynthesis.speak(u);}catch(e){}}
 pWin.angelSpeakText=function(txt, lang){ try{pWin.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(txt);u.lang=lang||'fr-FR';u.rate=0.9;pWin.speechSynthesis.speak(u);}catch(e){}}
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;600&display=swap');
.stApp {background:#FCFCF9!important; font-family:'DM Sans',sans-serif!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
[data-testid="stSidebar"]{background:#F5F3EF!important; border-right:1px solid #E8E3DC!important;}
.brain-video{width:120px;height:120px;border-radius:50%;object-fit:cover;box-shadow:0 0 40px rgba(224,122,79,0.25);border:2px solid #E07A4F;}
.angel-title{font-family:'Space Grotesk';font-size:40px;font-weight:700;letter-spacing:-2px;text-align:center;margin-top:12px;}
.neural{color:#E07A4F;font-size:10px;letter-spacing:3px;font-weight:700;text-align:center;margin-top:6px;}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    for p in [Path("brain.mp4"), Path(__file__).parent / "brain.mp4"]:
        if p.exists():
            b64=base64.b64encode(p.read_bytes()).decode()
            return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="font-size:80px;text-align:center">🧠</div>'

if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets"); st.stop()

# MEMOIRE
if "memory" not in st.session_state:
    st.session_state.memory={"prenom":"","niveau":"Premiere","historique":[]}
if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe=st.session_state.memory["niveau"]
if "mode" not in st.session_state: st.session_state.mode="chat"
if "lang_call" not in st.session_state: st.session_state.lang_call="Anglais"

# Mapping langue -> code vocal
LANG_CODES={"Anglais":"en-US","Espagnol":"es-ES","Allemand":"de-DE","Italien":"it-IT","Chinois":"zh-CN","Français":"fr-FR"}

def ask_groq(q, img=None, is_vocal=False):
    try:
        mem=st.session_state.memory
        mem_txt=f"Utilisateur: {mem.get('prenom','')} Niveau {mem.get('niveau')} Historique {mem.get('historique')[-3:]}"
        if is_vocal:
            sys_prompt=f"Tu es Angel tuteur vocal {st.session_state.lang_call}. {mem_txt}. Parle court 2 phrases, corrige doucement, réponds en {st.session_state.lang_call}."
        else:
            sys_prompt=f"Tu es Angel prof {st.session_state.classe}. {mem_txt}. Maths avec $ $ et $$ $$. Jamais le mot LaTeX."
        url="https://api.groq.com/openai/v1/chat/completions"
        headers={"Authorization":"Bearer "+KEY}
        if img:
            b64=base64.b64encode(img).decode()
            payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":sys_prompt+" Question:"+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist=[{"role":m["role"],"content":m["content"][:500]} for m in st.session_state.messages[-4:]]
            payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":sys_prompt}]+hist+[{"role":"user","content":q}]}
        r=requests.post(url,headers=headers,json=payload,timeout=60).json()
        return fix_latex(r["choices"][0]["message"]["content"])
    except Exception as e:
        return f"Erreur: {e}"

# SIDEBAR
with st.sidebar:
    st.markdown(f"<div style='text-align:center'>{get_video_html()}<div style='font-family:Space Grotesk;font-weight:700;margin-top:8px'>Angel AI</div></div>", unsafe_allow_html=True)
    st.session_state.memory["prenom"]=st.text_input("Prénom", value=st.session_state.memory["prenom"])

    st.markdown("### Mode")
    choix=st.radio("mode", ["💬 Chat Études","📞 Appel Vocal Langues"], label_visibility="collapsed")
    st.session_state.mode="vocal" if "Vocal" in choix else "chat"

    if st.session_state.mode=="vocal":
        st.session_state.lang_call=st.selectbox("Langue", list(LANG_CODES.keys()))

    st.markdown("### Niveau")
    for label, items in [("COLLEGE",["6e","5e","4e","3e"]),("LYCEE",["Seconde","Premiere","Terminale"]),("UNIV",["Licence 1","Master 1","Doctorat"])]:
        st.caption(label)
        cols=st.columns(3)
        for i,c in enumerate(items):
            with cols[i%3]:
                if st.button(c, key=f"cl_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                    st.session_state.classe=c
                    st.session_state.memory["niveau"]=c
                    st.rerun()
    if st.button("🗑️ Effacer mémoire", use_container_width=True):
        st.session_state.messages=[]
        st.session_state.memory={"prenom":"","niveau":"Premiere","historique":[]}
        st.rerun()

# HEADER
st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;margin:10px 0">
  {get_video_html()}
  <div class="angel-title">Angel AI</div>
  <div class="neural">NEURAL ENGINE • MEMOIRE ACTIVE • {st.session_state.memory.get('prenom','')}</div>
</div>
""", unsafe_allow_html=True)

# MODE CHAT
if st.session_state.mode=="chat":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(f'<div id="msg-{i}">{fix_latex(m["content"])}</div>', unsafe_allow_html=True)
            if m["role"]=="assistant":
                components.html("<script>try{window.parent.playDing();}catch(e){}</script>", height=0)
                code=LANG_CODES.get(st.session_state.lang_call,"fr-FR")
                components.html(f"""
                <button onclick="window.parent.angelSpeak('msg-{i}','{code}')" style="background:#0a0a0a;color:white;border:none;border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer">🔊 Lire</button>
                <button onclick="window.parent.angelStop()" style="background:#eee;border:none;border-radius:20px;padding:6px 10px;margin-left:6px">⏹️</button>
                """, height=40)

    with st.expander("📸 Photo devoir + Caméra", expanded=False):
        up=st.file_uploader("Importer", type=["jpg","png","jpeg"], label_visibility="collapsed")
        cam=st.camera_input("Caméra", label_visibility="collapsed")
        img=cam.getvalue() if cam else (up.getvalue() if up else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            rep=ask_groq("Explique étape par étape", img)
            st.session_state.messages+=[{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}]
            st.rerun()

    prompt=st.chat_input(f"Question {st.session_state.classe}...")
    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        st.session_state.memory["historique"].append(prompt[:80])
        rep=ask_groq(prompt)
        st.session_state.messages.append({"role":"assistant","content":rep})
        st.rerun()

# MODE VOCAL
else:
    st.info(f"📞 Mode Appel Vocal - {st.session_state.lang_call} - Parle et Angel te répond vocalement")

    for i,m in enumerate(st.session_state.messages[-8:]):
        with st.chat_message(m["role"]):
            st.markdown(fix_latex(m["content"]))
            if m["role"]=="assistant":
                safe_text=m["content"][:400].replace("`","").replace("'"," ").replace('"'," ").replace("\n"," ")
                code=LANG_CODES.get(st.session_state.lang_call,"en-US")
                components.html(f"""
                <button onclick="window.parent.angelSpeakText('{safe_text}', '{code}')" style="background:#0a0a0a;color:white;border:none;border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer;margin-top:6px">🔊 Réécouter en {st.session_state.lang_call}</button>
                """, height=40)

    vocal_q=st.chat_input(f"Parle en {st.session_state.lang_call}... (écris, Angel va répondre vocalement)")
    if vocal_q:
        st.session_state.messages.append({"role":"user","content":vocal_q})
        rep=ask_groq(vocal_q, is_vocal=True)
        st.session_state.messages.append({"role":"assistant","content":rep})
        safe_rep=rep[:500].replace("`","").replace("'"," ").replace('"'," ").replace("\n"," ")
        code=LANG_CODES.get(st.session_state.lang_call,"en-US")
        components.html(f"<script>window.parent.angelSpeakText('{safe_rep}', '{code}')</script>", height=0)
        st.rerun()
