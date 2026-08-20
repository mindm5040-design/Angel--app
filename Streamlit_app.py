import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

st.markdown("""
<style>
.stApp {background:#f8f9ff!important;}
header, footer {visibility:hidden!important;}

.classe-title {text-align:center; font-size:22px; font-weight:800; color:#0a27a6; margin:10px 0;}
.classe-subtitle {text-align:center; color:#666; font-size:13px; margin-bottom:15px;}

/* CHIPS NIVEAUX */
div[data-testid="stButton"] > button {
    border-radius:12px!important; font-weight:600!important; height:48px!important;
    border:1.5px solid #e0e4ff!important; background:white!important; color:#0a27a6!important;
    transition:0.2s;
}
div[data-testid="stButton"] > button:hover {background:#eef1ff!important; transform:scale(1.03);}
div[data-testid="stButton"] > button[kind="primary"] {
    background:#0a27a6!important; color:white!important; border:none!important;
    box-shadow:0 4px 12px rgba(10,39,166,0.3)!important;
}

/* CATEGORIES */
.cat {font-weight:700; font-size:12px; letter-spacing:1px; color:#0a27a6; margin:18px 0 8px 4px; opacity:0.7;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if "classe" not in st.session_state: st.session_state.classe = None
if "messages" not in st.session_state: st.session_state.messages = []

def ask(q, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof niveau {st.session_state.classe}"},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=60).json()
    return r["choices"][0]["message"]["content"]

# SI PAS DE CLASSE CHOISIE -> ECRAN SELECTION
if st.session_state.classe is None:
    st.markdown("<div class='classe-title'>🕊️ Bienvenue sur Angel</div>", unsafe_allow_html=True)
    st.markdown("<div class='classe-subtitle'>Choisis ton niveau pour commencer</div>", unsafe_allow_html=True)

    st.markdown("<div class='cat'>📘 COLLÈGE</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for i, cl in enumerate(["6e","5e","4e","3e"]):
        with [c1,c2,c3,c4][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div class='cat'>📗 LYCÉE</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for i, cl in enumerate(["Seconde","Première","Terminale"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div class='cat'>🎓 UNIVERSITÉ</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for i, cl in enumerate(["Licence 1","Licence 2","Licence 3"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    c1,c2,c3 = st.columns(3)
    for i, cl in enumerate(["Master 1","Master 2","Doctorat"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.stop()

# SI CLASSE CHOISIE -> CHAT
st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><b>🕊️ Angel • {st.session_state.classe}</b><div></div></div>", unsafe_allow_html=True)
if st.button("↩️ Changer de niveau"):
    st.session_state.classe=None; st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

with st.expander("📷 Photo"):
    up=st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam=st.camera_input(" ", label_visibility="collapsed")
    img = cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser", type="primary"):
        rep=ask("Explique", img)
        st.session_state.messages+=[{"role":"user","content":"📷 Photo"},{"role":"assistant","content":rep}]
        st.rerun()

prompt = st.chat_input("Message")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
