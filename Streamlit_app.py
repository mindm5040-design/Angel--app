import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel AI", page_icon="🕊️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
.stApp {background: radial-gradient(1200px at 20% -10%, #dbe4ff 0%, #f8f9ff 50%, #ffffff 100%)!important; font-family:'Outfit', sans-serif;}
header, footer {visibility:hidden!important;}

/* TITRE ANIME */
.title-ai {
  text-align:center; font-size:32px; font-weight:800;
  background: linear-gradient(90deg, #0a27a6, #5b7fff, #0a27a6);
  background-size:200% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  animation: shine 3s linear infinite; margin-top:10px;
}
@keyframes shine {to {background-position:200% center;}}
.subtitle {text-align:center; color:#6b7280; font-size:14px; margin-bottom:20px; animation: fadeIn 0.8s ease;}

/* CATEGORIES */
.cat {font-size:11px; font-weight:800; letter-spacing:2px; color:#0a27a6; opacity:0.6; margin:22px 0 10px 4px; animation: slideUp 0.5s ease;}

/* BOUTONS CLASSES - EFFET IA */
div[data-testid="stButton"] > button {
  border-radius:16px!important; height:56px!important; font-weight:700!important; font-size:15px!important;
  background: rgba(255,255,255,0.8)!important; backdrop-filter: blur(12px)!important;
  border:1px solid rgba(10,39,166,0.12)!important; color:#0a27a6!important;
  box-shadow: 0 2px 8px rgba(10,39,166,0.06)!important;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1)!important;
  animation: slideUp 0.6s ease backwards;
}
div[data-testid="stButton"] > button:hover {
  transform: translateY(-3px) scale(1.02)!important;
  background: white!important; border-color:#0a27a6!important;
  box-shadow: 0 12px 24px rgba(10,39,166,0.18)!important;
}
div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(135deg, #0a27a6 0%, #3a5bff 100%)!important;
  color:white!important; border:none!important;
  box-shadow: 0 8px 20px rgba(10,39,166,0.35)!important;
}
div[data-testid="stButton"] > button:active {transform: scale(0.97)!important;}

@keyframes slideUp {from {opacity:0; transform:translateY(12px);} to {opacity:1; transform:translateY(0);}}
@keyframes fadeIn {from {opacity:0;} to {opacity:1;}}

@keyframes pulse {
  0% {box-shadow:0 0 0 0 rgba(10,39,166,0.4);}
  70% {box-shadow:0 0 0 12px rgba(10,39,166,0);}
  100% {box-shadow:0 0 0 0 rgba(10,39,166,0);}
}
.active-class {animation: pulse 2s infinite;}

/* CHAT BUBBLES PRO */
[data-testid="stChatMessage"] {animation: slideUp 0.3s ease;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if "classe" not in st.session_state: st.session_state.classe=None
if "messages" not in st.session_state: st.session_state.messages=[]

def ask(q, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel IA, prof niveau {st.session_state.classe}, design pro"},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=60).json()
    return r["choices"][0]["message"]["content"]

# ECRAN SELECTION
if st.session_state.classe is None:
    st.markdown("<div class='title-ai'>🕊️ Angel AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Intelligence qui t'explique • Choisis ton niveau</div>", unsafe_allow_html=True)

    st.markdown("<div class='cat'>COLLÈGE</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for i, cl in enumerate(["6e","5e","4e","3e"]):
        with [c1,c2,c3,c4][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div class='cat'>LYCÉE</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for i, cl in enumerate(["Seconde","Première","Terminale"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div class='cat'>UNIVERSITÉ • LICENCE</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for i, cl in enumerate(["Licence 1","Licence 2","Licence 3"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div class='cat'>UNIVERSITÉ • MASTER & DOCTORAT</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for i, cl in enumerate(["Master 1","Master 2","Doctorat"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True, type="primary" if cl=="Doctorat" else "secondary"):
                st.session_state.classe=cl; st.rerun()

    st.stop()

# CHAT PRO
st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; padding:8px 0;'><div style='font-weight:800; color:#0a27a6;'>🕊️ Angel • {st.session_state.classe}</div><div style='font-size:12px; color:#6b7280;'>IA • En ligne</div></div>", unsafe_allow_html=True)

if st.button("↩️ Changer de niveau", use_container_width=False):
    st.session_state.classe=None; st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

with st.expander("📷 Photo + 📷 Caméra"):
    up=st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam=st.camera_input(" ", label_visibility="collapsed")
    img = cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("✨ Analyser avec Angel IA", type="primary", use_container_width=True):
        rep=ask("Explique", img)
        st.session_state.messages+=[{"role":"user","content":"📷 Photo"},{"role":"assistant","content":rep}]
        st.rerun()

prompt = st.chat_input("Demande à Angel IA...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
