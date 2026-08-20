import streamlit as st
import requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

FILE = "angel_memory.json"
KEY = st.secrets.get("GROQ_API_KEY","").strip()

def load_chats():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
        # Si ancien format dict par classe -> on convertit / on reset
        if isinstance(data, dict):
            return []
        # On garde seulement les messages valides
        clean = []
        for m in data:
            if isinstance(m, dict) and "role" in m and "content" in m:
                if m["role"] in ["user","assistant"]:
                    clean.append(m)
        return clean
    except:
        return []

def save_chats(chats):
    try:
        with open(FILE,"w",encoding="utf-8") as f:
            json.dump(chats, f, ensure_ascii=False, indent=2)
    except:
        pass

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
if "tool" not in st.session_state:
    st.session_state.tool = None

def ask_groq(question, img_bytes=None):
    try:
        if img_bytes:
            b64 = base64.b64encode(img_bytes).decode()
            body = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }]
            }
        else:
            body = {
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": "Tu es Angel, prof qui explique simple."},
                    {"role": "user", "content": question}
                ]
            }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json=body,
            timeout=40
        ).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

# AFFICHAGE CHAT SECURISE
for m in st.session_state.chats:
    try:
        role = m.get("role","user")
        if role not in ["user","assistant"]:
            role = "user"
        with st.chat_message(role):
            st.markdown(m.get("content",""))
    except:
        continue

if st.session_state.tool == "photo":
    with st.container(border=True):
        up = st.file_uploader("Photo", type=["jpg","png"], label_visibility="collapsed")
        cam = st.camera_input("Caméra", label_visibility="collapsed")
        img = cam.getvalue() if cam else (up.getvalue() if up else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            ans = ask_groq("Résous cet exercice", img)
            st.session_state.chats.append({"role":"user","content":"📷 Photo"})
            st.session_state.chats.append({"role":"assistant","content":ans})
            save_chats(st.session_state.chats)
            st.session_state.tool = None
            st.rerun()
        if st.button("Fermer"):
            st.session_state.tool = None
            st.rerun()

if st.session_state.tool == "vocal":
    with st.container(border=True):
        aud = st.audio_input("Vocal", label_visibility="collapsed")
        if aud:
            try:
                files = {"file": ("a.wav", aud.getvalue(), "audio/wav")}
                data = {"model": "whisper-large-v3", "language": "fr"}
                txt = requests.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {KEY}"},
                    files=files, data=data, timeout=60
                ).json().get("text","")
                if txt:
                    st.session_state.chats.append({"role":"user","content":txt})
                    st.session_state.chats.append({"role":"assistant","content":ask_groq(txt)})
                    save_chats(st.session_state.chats)
                    st.session_state.tool = None
                    st.rerun()
            except:
                pass
        if st.button("Fermer"):
            st.session_state.tool = None
            st.rerun()

st.markdown("---")

# BARRE COMME TON IMAGE : + 📷 🖼️ 🎙️ [Message] ➤
c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,5,1])

with c1:
    if st.button("➕", key="plus"):
        st.session_state.tool = "photo"
        st.rerun()
with c2:
    if st.button("📷", key="cam"):
        st.session_state.tool = "photo"
        st.rerun()
with c3:
    if st.button("🖼️", key="gal"):
        st.session_state.tool = "photo"
        st.rerun()
with c4:
    if st.button("🎙️", key="mic"):
        st.session_state.tool = "vocal"
        st.rerun()
with c5:
    q = st.text_input("msg", placeholder="Message", label_visibility="collapsed", key="input_msg")
with c6:
    st.button("➤", key="send", type="primary")

if q and q.strip():
    if q!= st.session_state.get("last_q",""):
        st.session_state.last_q = q
        st.session_state.chats.append({"role":"user","content":q})
        st.session_state.chats.append({"role":"assistant","content":ask_groq(q)})
        save_chats(st.session_state.chats)
        st.rerun()
