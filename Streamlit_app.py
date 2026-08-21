import streamlit as st
import requests
import base64
import os
from pathlib import Path
from PIL import Image
import io

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

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
        return ""
    # version simple sans regex qui plante
    text = text.replace("\\[", "$$")
    text = text.replace("\\]", "$$")
    text = text.replace("\\(", "$")
    text = text.replace("\\)", "$")
    return text

st.markdown("""
<style>
.stApp {background:#FCFCF9!important;}
header, footer, #MainMenu,.stDeployButton {visibility:hidden!important;}
.brain-video {width:140px; height:140px; border-radius:50%; object-fit:cover; box-shadow:0 0 40px rgba(224,122,79,0.3); border:2px solid #E07A4F;}
div[data-testid="stButton"] > button {background: white!important; border:1px solid rgba(0,0,0,0.06)!important; border-radius:18px!important; height:72px!important; font-weight:600!important;}
button[kind="primary"] {background:#0a0a0a!important; color:white!important;}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    p = Path("brain.mp4")
    if p.exists():
        try:
            b64 = base64.b64encode(p.read_bytes()).decode()
            return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
        except:
            pass
    return '<div style="font-size:90px; text-align:center;">🧠</div>'

st.markdown(f"""
<div style="text-align:center; margin:10px 0;">
  {get_video_html()}
  <div style="font-size:44px; font-weight:700;">Angel AI</div>
  <div style="color:#E07A4F; font-size:10px; letter-spacing:3px; font-weight:700;">NEURAL ENGINE • ACTIVE</div>
</div>
""", unsafe_allow_html=True)

if not KEY:
    st.warning("Mets GROQ_API_KEY dans Secrets")
    st.stop()

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Master 1"

def ask_groq(q, img=None):
    try:
        system_prompt = f"Tu es Angel, prof niveau {st.session_state.classe}. Maths avec $$ $$."
        if img:
            im = Image.open(io.BytesIO(img)).convert("RGB")
            im.thumbnail((900, 900))
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=65)
            b64 = base64.b64encode(buf.getvalue()).decode()
            payload={
                "model":"llama-3.2-90b-vision-preview",
                "messages":[{
                    "role":"user",
                    "content":[
                        {"type":"text","text": system_prompt + " " + q},
                        {"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}
                    ]
                }],
                "max_tokens": 1200
            }
        else:
            payload={
                "model":"llama-3.3-70b-versatile",
                "messages":[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":q}
                ],
                "max_tokens": 1000
            }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + KEY, "Content-Type":"application/json"},
            json=payload,
            timeout=90
        )
        data = r.json()
        if "choices" not in data:
            return f"Groq: {data}"
        return fix_latex(data["choices"][0]["message"]["content"])
    except Exception as e:
        return f"Erreur: {e}"

with st.expander(f"Niveau: {st.session_state.classe}", expanded=False):
    cols=st.columns(3)
    levels=["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]
    for i,c in enumerate(levels):
        with cols[i%3]:
            if st.button(c, key=f"cl_{i}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c
                st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(fix_latex(m["content"]))

with st.expander("📸 Photo devoir"):
    up=st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam=st.camera_input(" ", label_visibility="collapsed")
    img_bytes=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img_bytes and st.button("Analyser", type="primary", use_container_width=True):
        with st.spinner("Analyse..."):
            rep=ask_groq("Explique cet exercice etape par etape", img_bytes)
            st.session_state.messages+=[{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}]
            st.rerun()

prompt=st.chat_input(f"Question niveau {st.session_state.classe}...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask_groq(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
