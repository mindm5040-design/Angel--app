import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

KEY = st.secrets.get("GROQ_API_KEY","")
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans les Secrets")
    st.stop()

if "chats" not in st.session_state:
    st.session_state.chats = []
if "classe" not in st.session_state:
    st.session_state.classe = "Master 1"
if "tool" not in st.session_state:
    st.session_state.tool = None

def ask(q, img=None):
    try:
        if img:
            b64 = base64.b64encode(img).decode()
            body = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
        else:
            body = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof {st.session_state.classe}"},{"role":"user","content":q}]}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=50).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

# HEADER
st.markdown(f"**🕊️ Angel • {st.session_state.classe}** - {len(st.session_state.chats)} messages")
with st.expander(f"📚 Classe : {st.session_state.classe}"):
    for c in ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]:
        if st.button(c, key=c, use_container_width=True):
            st.session_state.classe = c
            st.rerun()

# CHAT - AFFICHAGE SIMPLE QUI NE PEUT PAS CACHER
for msg in st.session_state.chats:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# OUTILS
if st.session_state.tool == "photo":
    st.info("Envoie ta photo")
    up = st.file_uploader("Fichier", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam = st.camera_input("Camera", label_visibility="collapsed")
    img = None
    if cam: img = cam.getvalue()
    elif up: img = up.getvalue()
    if img and st.button("Analyser", type="primary"):
        ans = ask("Résous et explique", img)
        st.session_state.chats.append({"role":"user","content":"📷 Photo"})
        st.session_state.chats.append({"role":"assistant","content":ans})
        st.session_state.tool = None
        st.rerun()
    if st.button("Fermer"):
        st.session_state.tool = None
        st.rerun()

if st.session_state.tool == "vocal":
    st.info("Parle")
    aud = st.audio_input("Vocal", label_visibility="collapsed")
    if aud:
        files = {"file": ("a.wav", aud.getvalue(), "audio/wav")}
        data = {"model":"whisper-large-v3","language":"fr"}
        txt = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",headers={"Authorization":f"Bearer {KEY}"},files=files,data=data,timeout=60).json().get("text","")
        if txt:
            st.session_state.chats.append({"role":"user","content":txt})
            st.session_state.chats.append({"role":"assistant","content":ask(txt)})
            st.session_state.tool = None
            st.rerun()
    if st.button("Fermer"):
        st.session_state.tool = None
        st.rerun()

# BARRE EN BAS - TOUJOURS VISIBLE ET HORIZONTALE
st.divider()
c1,c2,c3,c4,c5,c6 = st.columns([1,1,1,1,4,1], gap="small")
with c1:
    if st.button("➕", key="b1"): st.session_state.tool="photo"; st.rerun()
with c2:
    if st.button("📷", key="b2"): st.session_state.tool="photo"; st.rerun()
with c3:
    if st.button("🖼️", key="b3"): st.session_state.tool="photo"; st.rerun()
with c4:
    if st.button("🎙️", key="b4"): st.session_state.tool="vocal"; st.rerun()
with c5:
    q = st.text_input("Message", placeholder="Message", label_visibility="collapsed", key="q")
with c6:
    send = st.button("➤", key="send", type="primary")

if send and q.strip():
    st.session_state.chats.append({"role":"user","content":q})
    st.session_state.chats.append({"role":"assistant","content":ask(q)})
    st.rerun()
