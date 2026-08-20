import streamlit as st, requests, base64, json, os, uuid
from datetime import datetime

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
.stApp {background:#fcfaf8!important;}
section[data-testid="stSidebar"] {background:#f5f2ed!important;}
div[data-testid="stChatMessages"] {max-width:740px; margin:0 auto; gap:16px!important; padding-bottom:60px!important;}
.stChatMessage p {font-size:15px!important; line-height:1.7!important;}
.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px!important; padding:12px 16px!important;
}
div[data-testid="stChatInput"] {max-width:740px; margin:0 auto; border-radius:24px!important; background:white!important;}
</style>
""", unsafe_allow_html=True)

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
FILE = "angel_memory.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {c: [] for c in CLASSES}

def save():
    with open(FILE,"w",encoding="utf-8") as f: json.dump(st.session_state.chats, f, ensure_ascii=False, indent=2)

if "chats" not in st.session_state: st.session_state.chats = load()
if "classe" not in st.session_state: st.session_state.classe = "3e"

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def ask(q, classe, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}"},{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}. Programme strict {classe}."},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {KEY}"}, json=payload, timeout=40).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur"

# SIDEBAR
with st.sidebar:
    st.markdown("## 🕊️ Angel")
    st.caption(f"Salle actuelle: **{st.session_state.classe}**")

    st.markdown("**Changer de classe**")
    c1,c2 = st.columns(2)
    for i, cl in enumerate(CLASSES):
        with (c1 if i%2==0 else c2):
            if st.button(cl, key=f"cl_{cl}", use_container_width=True, type="primary" if cl==st.session_state.classe else "secondary"):
                st.session_state.classe = cl
                st.rerun()

    st.markdown("---")
    st.markdown("**📸 Photo**")
    up = st.file_uploader("Importer", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam = st.camera_input("Caméra", label_visibility="collapsed")

    st.markdown("**🎙️ Audio**")
    aud = st.audio_input("Vocal", label_visibility="collapsed")

    st.markdown("---")
    if st.button("🗑️ Vider cette salle", use_container_width=True):
        st.session_state.chats[st.session_state.classe]=[]
        save(); st.rerun()

# MAIN
cl = st.session_state.classe
st.markdown(f"<div style='max-width:740px; margin:0 auto; padding:8px 0;'><b>🕊️ Angel • {cl}</b> <span style='color:#888; font-size:13px;'>• {len(st.session_state.chats[cl])} messages sauvegardés</span></div>", unsafe_allow_html=True)

for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Photo
img_data = cam.getvalue() if cam else (up.getvalue() if up and hasattr(up,'getvalue') else None)
if img_data and st.button(f"📸 Analyser cette photo en {cl}", use_container_width=True):
    with st.spinner("Angel analyse..."):
        ans = ask(f"Résous cet exercice niveau {cl}", cl, img_data)
        st.session_state.chats[cl].extend([{"role":"user","content":"📸 Photo envoyée"},{"role":"assistant","content":ans}])
        save(); st.rerun()

# Audio
if aud:
    try:
        files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
        txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
        if txt and len(txt)>2:
            st.session_state.chats[cl].append({"role":"user","content":f"🎙️ {txt}"})
            st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)})
            save(); st.rerun()
    except: pass

# Texte
q = st.chat_input(f"Écris à Angel en {cl}...")
if q:
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
