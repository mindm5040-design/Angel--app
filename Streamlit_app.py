import streamlit as st, requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
.stApp{background:#0a0d13;color:#edeff3}
section[data-testid="stSidebar"]{background:#10141c}
.stChatMessage{border-radius:16px}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
LEVELS = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Master 1"]
KEY = st.secrets.get("GROQ_API_KEY","").strip()

def call_text(q, level):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={"model":"openai/gpt-oss-20b","messages":[
                {"role":"system","content":f"Tu es Angel, prof d'élite niveau {level}. Pédagogue, clair, en français."},
                {"role":"user","content":q}]}, timeout=30).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e} - {r if 'r' in locals() else ''}"

def call_vision(q, img_bytes, level):
    b64 = base64.b64encode(img_bytes).decode()
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={
            "model":"meta-llama/llama-4-scout-17b-16e-instruct",
            "messages":[
                {"role":"system","content":f"Tu es Angel, prof niveau {level}. Analyse l'image."},
                {"role":"user","content":[
                    {"type":"text","text":q},
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                ]}
            ]
        }, timeout=60).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur vision: {r}"

def transcribe(audio_bytes):
    try:
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"model":"whisper-large-v3", "language":"fr"}
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json()
        return r.get("text","")
    except Exception as e:
        return ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🕊️ Angel")
    level = st.selectbox("Niveau", LEVELS, index=5)
    st.markdown("---")
    st.markdown("### 📸 Photo d'exo")
    img_file = st.file_uploader("Upload", type=["jpg","jpeg","png"], label_visibility="collapsed")
    cam = st.camera_input("Caméra", label_visibility="collapsed")

    st.markdown("### 🎙️ Vocal")
    audio = st.audio_input("Parle", label_visibility="collapsed")

    st.markdown("---")
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages=[]; st.rerun()

# --- MAIN CHAT ---
st.markdown("## 🕊️ Angel")
st.caption(f"Mode {level} • Texte + Photo + Vocal • Ultra rapide")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Traitement Photo
final_img = cam if cam else img_file
if final_img and st.button("📸 Analyser cette photo", use_container_width=True):
    with st.chat_message("user"):
        st.image(final_img, width=300)
        st.write("Analyse cet exercice")
    q = "Explique et résous l'exercice sur cette image étape par étape"
    st.session_state.messages.append({"role":"user","content":"📸 Image envoyée"})
    ans = call_vision(q, final_img.getvalue(), level)
    st.session_state.messages.append({"role":"assistant","content":ans})
    st.rerun()

# Traitement Vocal
if audio:
    texte = transcribe(audio.getvalue())
    if texte:
        st.session_state.messages.append({"role":"user","content":f"🎙️ {texte}"})
        ans = call_text(texte, level)
        st.session_state.messages.append({"role":"assistant","content":ans})
        st.rerun()

# Chat normal
q = st.chat_input("Écris, parle ou envoie une photo...")
if q:
    st.session_state.messages.append({"role":"user","content":q})
    with st.chat_message("user"): st.write(q)
    with st.chat_message("assistant"):
        with st.spinner("Angel analyse..."):
            ans = call_text(q, level)
            st.write(ans)
    st.session_state.messages.append({"role":"assistant","content":ans})
