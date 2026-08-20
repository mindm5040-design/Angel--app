import streamlit as st
import requests
import base64
import os
from pathlib import Path

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")

KEY = get_groq_key()

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
        if img:
            b64=base64.b64encode(img).decode()
            payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":f"[{st.session_state.classe}] {q}"},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
        else:
            payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof niveau {st.session_state.classe}"},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=payload,timeout=60).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

with st.expander(f"Niveau: {st.session_state.classe}", expanded=False):
    for label, items in [("COLLEGE",["6e","5e","4e","3e"]),("LYCEE",["Seconde","Premiere","Terminale"]),("UNIVERSITE",["Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"])]:
        st.markdown(f'<div style="font-size:10px; letter-spacing:2px; color:#999; font-weight:700; margin:10px 0 6px;">{label}</div>', unsafe_allow_html=True)
        cols=st.columns(3)
        for i,c in enumerate(items):
            with cols[i%3]:
                if st.button(c, key=f"cl_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                    st.session_state.classe=c; st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

with st.expander("📸 Photo devoir"):
    up=st.file_uploader(" ", type=["jpg","png"], label_visibility="collapsed")
    cam=st.camera_input(" ", label_visibility="collapsed")
    img=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser", type="primary", use_container_width=True):
        rep=ask_groq("Explique cet exercice etape par etape", img)
        st.session_state.messages+=[{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}]
        st.rerun()

prompt=st.chat_input(f"Question niveau {st.session_state.classe}...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask_groq(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
