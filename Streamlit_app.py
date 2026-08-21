import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Source+Serif+4:wght@400;500&display=swap');
.stApp {background:#fcfaf8!important;}
section[data-testid="stSidebar"] {background:#f5f2ed!important;}
div[data-testid="stChatMessages"] {max-width:760px; margin:0 auto; gap:1.2rem!important;}
.stChatMessage {background:transparent!important; border:none!important;}
.stChatMessage p {font-family:'Source Serif 4', serif!important; font-size:15px!important; line-height:1.75!important;}
div[data-testid="stChatInput"] {max-width:760px; margin:0 auto; background:white!important; border:1px solid #e8e0d0!important; border-radius:24px!important;}
</style>
""", unsafe_allow_html=True)

CLASSES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Licence": ["Licence 1", "Licence 2", "Licence 3"],
    "Master & Doctorat": ["Master 1", "Master 2", "Doctorat"]
}
ALL_CLASSES = [c for v in CLASSES.values() for c in v]

FILE = "angel_memory.json"
def load_memory():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {c: [] for c in ALL_CLASSES}

def save_memory():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.class_chats, f, ensure_ascii=False, indent=2)

if "class_chats" not in st.session_state:
    st.session_state.class_chats = load_memory()
if "active_classe" not in st.session_state:
    st.session_state.active_classe = "3e"

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def call_text(q, classe):
    sys = f"Tu es Angel, prof de {classe}. Programme strict {classe} uniquement. Si hors programme, refuse poliment. Francais clair, aere."
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":sys},{"role":"user","content":q}]}, timeout=30).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur {r}"

def call_vision(q, img_bytes, classe):
    b64 = base64.b64encode(img_bytes).decode()
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[
            {"role":"system","content":f"Tu es Angel, prof de {classe}. Analyse l'image."},
            {"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
        ]}, timeout=60).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur vision {r}"

def transcribe(audio_bytes):
    try:
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}; data = {"model":"whisper-large-v3","language":"fr"}
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json()
        return r.get("text","")
    except: return ""

with st.sidebar:
    st.markdown("## 🕊️ Angel")
    st.caption("Mémoire activée • Reste même si tu quittes")
    for cycle, liste in CLASSES.items():
        st.markdown(f"**{cycle}**")
        cols = st.columns(2)
        for i, c in enumerate(liste):
            with cols[i % 2]:
                active = st.session_state.active_classe == c
                if st.button(f"{'🔵 ' if active else ''}{c}", key=f"btn_{c}", use_container_width=True, type="primary" if active else "secondary"):
                    st.session_state.active_classe = c
                    st.rerun()
    st.markdown("---")
    st.markdown("**📸 Photo**")
    up = st.file_uploader("Importer", type=["jpg","jpeg","png"], label_visibility="collapsed", key="up")
    cam = st.camera_input("Caméra", label_visibility="collapsed", key="cam")
    st.markdown("**🎙️ Vocal**")
    aud = st.audio_input("Enregistrer", label_visibility="collapsed", key="aud")
    if st.button("🗑️ Vider cette salle", use_container_width=True):
        st.session_state.class_chats[st.session_state.active_classe] = []
        save_memory(); st.rerun()

active = st.session_state.active_classe
st.markdown(f"<div style='max-width:760px; margin:0 auto;'><span style='background:#1a1a1a; color:white; padding:6px 14px; border-radius:20px; font-size:13px;'>🕊️ Angel • Salle {active}</span></div>", unsafe_allow_html=True)

for m in st.session_state.class_chats[active]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

img = cam or up
if img and st.button(f"📸 Analyser avec Angel {active}"):
    with st.spinner("Angel analyse..."):
        ans = call_vision("Résous cet exercice étape par étape, niveau "+active, img.getvalue(), active)
        st.session_state.class_chats[active].append({"role":"user","content":f"📸 [Photo en {active}]"})
        st.session_state.class_chats[active].append({"role":"assistant","content":ans})
        save_memory(); st.rerun()

if aud:
    txt = transcribe(aud.getvalue())
    if txt and len(txt) > 2:
        st.session_state.class_chats[active].append({"role":"user","content":f"🎙️ {txt}"})
        ans = call_text(txt, active)
        st.session_state.class_chats[active].append({"role":"assistant","content":ans})
        save_memory(); st.rerun()

q = st.chat_input(f"Message à Angel en {active}...")
if q:
    st.session_state.class_chats[active].append({"role":"user","content":q})
    ans = call_text(q, active)
    st.session_state.class_chats[active].append({"role":"assistant","content":ans})
    save_memory(); st.rerun()
