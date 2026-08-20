import streamlit as st
import requests, base64, os, json

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

# SUPPRESSION AUTO DU FICHIER CORROMPU QUI CAUSE TON ERREUR
if os.path.exists("angel_memory.json"):
    try: os.remove("angel_memory.json")
    except: pass

KEY = st.secrets.get("GROQ_API_KEY","")
if "chats" not in st.session_state:
    st.session_state.chats = []
if "tool" not in st.session_state:
    st.session_state.tool = None
if "classe" not in st.session_state:
    st.session_state.classe = "Master 1"

def ask(q, img=None):
    if img:
        b64 = base64.b64encode(img).decode()
        body = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof {st.session_state.classe}"},{"role":"user","content":q}]}
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=50).json()
    return r["choices"][0]["message"]["content"]

st.write(f"**🕊️ Angel • {st.session_state.classe}** - {len(st.session_state.chats)} messages")

with st.expander(f"📚 Classe : {st.session_state.classe}"):
    for c in ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]:
        if st.button(c, key=c):
            st.session_state.classe = c
            st.rerun()

# AFFICHAGE SECURISE - NE PLANTE PLUS
for m in st.session_state.chats:
    try:
        if isinstance(m, dict) and "content" in m:
            role = m.get("role","user")
            if role not in ["user","assistant"]: role="user"
            with st.chat_message(role):
                st.write(m["content"])
    except:
        continue

if st.session_state.tool == "photo":
    up = st.file_uploader("Photo", type=["jpg","png","jpeg"])
    cam = st.camera_input("Camera")
    img = cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser", type="primary"):
        st.session_state.chats.append({"role":"user","content":"📷 Photo"})
        st.session_state.chats.append({"role":"assistant","content":ask("Explique cet exercice", img)})
        st.session_state.tool=None
        st.rerun()
    if st.button("Fermer"): st.session_state.tool=None; st.rerun()

if st.session_state.tool == "vocal":
    aud = st.audio_input("Parle")
    if aud:
        files={"file":("a.wav",aud.getvalue(),"audio/wav")}
        data={"model":"whisper-large-v3","language":"fr"}
        txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions",headers={"Authorization":f"Bearer {KEY}"},files=files,data=data,timeout=60).json().get("text","")
        if txt:
            st.session_state.chats.append({"role":"user","content":txt})
            st.session_state.chats.append({"role":"assistant","content":ask(txt)})
            st.session_state.tool=None
            st.rerun()
    if st.button("Fermer"): st.session_state.tool=None; st.rerun()

st.divider()
c1,c2,c3,c4,c5,c6 = st.columns([1,1,1,1,4,1])
with c1:
    if st.button("➕"): st.session_state.tool="photo"; st.rerun()
with c2:
    if st.button("📷"): st.session_state.tool="photo"; st.rerun()
with c3:
    if st.button("🖼️"): st.session_state.tool="photo"; st.rerun()
with c4:
    if st.button("🎙️"): st.session_state.tool="vocal"; st.rerun()
with c5:
    q = st.text_input("msg", placeholder="Message", label_visibility="collapsed")
with c6:
    if st.button("➤", type="primary"):
        if q.strip():
            st.session_state.chats.append({"role":"user","content":q})
            st.session_state.chats.append({"role":"assistant","content":ask(q)})
            st.rerun()
