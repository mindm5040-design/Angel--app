import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

# --- DESIGN MESSENGER ---
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
header, footer, #MainMenu {visibility:hidden!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}
.stChatMessage {border:none!important; background:transparent!important;}
div[data-testid="stChatMessageContent"] {padding:0!important;}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{
    background:#0a27a6!important; color:white!important;
    border-radius:18px 18px 4px 18px!important; padding:10px 14px!important; max-width:80%; margin-left:auto;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"]{
    background:#f0f2f5!important; color:black!important;
    border-radius:18px 18px 18px 4px!important; padding:10px 14px!important; max-width:80%;
}
div[data-testid="stBottom"] > div {background:white!important; border-top:1px solid #e4e6eb!important; padding:8px!important;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets"); st.stop()

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","L1","L2","L3","M1","M2","Doctorat"]
if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="M1"
if "tool" not in st.session_state: st.session_state.tool=None

def ask(q, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":f"[{st.session_state.classe}] {q}"},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof niveau {st.session_state.classe}, tu expliques clair et simple"},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=60).json()
    return r["choices"][0]["message"]["content"]

st.markdown(f"<div style='text-align:center; padding:10px; font-weight:700;'>Angel - {st.session_state.classe}</div>", unsafe_allow_html=True)

cols=st.columns(len(CLASSES), gap="small")
for i,c in enumerate(CLASSES):
    with cols[i]:
        if st.button(c, key=f"c_{c}"):
            st.session_state.classe=c
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if st.session_state.tool=="photo":
    with st.container(border=True):
        up=st.file_uploader("Galerie", type=["jpg","png","jpeg"], label_visibility="collapsed")
        cam=st.camera_input("Camera", label_visibility="collapsed")
        img = cam.getvalue() if cam else (up.getvalue() if up else None)
        c1,c2=st.columns(2)
        with c1:
            if img and st.button("Analyser", type="primary", use_container_width=True):
                rep=ask("Explique cet exercice", img)
                st.session_state.messages+= [{"role":"user","content":"Photo"},{"role":"assistant","content":rep}]
                st.session_state.tool=None; st.rerun()
        with c2:
            if st.button("Fermer", use_container_width=True):
                st.session_state.tool=None; st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        aud=st.audio_input("Parle", label_visibility="collapsed")
        if aud:
            files={"file":("a.wav", aud.getvalue(), "audio/wav")}
            data={"model":"whisper-large-v3","language":"fr"}
            txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions",headers={"Authorization":f"Bearer {KEY}"},files=files,data=data,timeout=60).json().get("text","")
            if txt:
                rep=ask(txt)
                st.session_state.messages+= [{"role":"user","content":txt},{"role":"assistant","content":rep}]
                st.session_state.tool=None; st.rerun()
        if st.button("Fermer"): st.session_state.tool=None; st.rerun()

st.divider()
c1,c2,c3,c4,c5,c6 = st.columns([1,1,1,1,4,1], gap="small")
with c1:
    if st.button("+"): st.session_state.tool="photo"; st.rerun()
with c2:
    if st.button("Photo"): st.session_state.tool="photo"; st.rerun()
with c3:
    if st.button("Img"): st.session_state.tool="photo"; st.rerun()
with c4:
    if st.button("Mic"): st.session_state.tool="vocal"; st.rerun()
with c5:
    q=st.text_input("msg", placeholder="Message", label_visibility="collapsed", key="input_q")
with c6:
    if st.button(">", type="primary"):
        if q and q.strip():
            rep=ask(q)
            st.session_state.messages+= [{"role":"user","content":q},{"role":"assistant","content":rep}]
            st.rerun()
