import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

# --- ULTRA HIGH-TECH DESIGN ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap');
.stApp {
  background: #0b1020!important;
  background-image:
    radial-gradient(at 20% 20%, #0a27a6 0px, transparent 50%),
    radial-gradient(at 80% 0%, #00e5ff22 0px, transparent 50%),
    radial-gradient(at 50% 100%, #1e3a8a44 0px, transparent 60%)!important;
  font-family:'Space Grotesk', sans-serif!important;
}
header, footer, #MainMenu {visibility:hidden!important;}

/* TITRE NEON QUI PULSE */
.angel-title {
  text-align:center; font-size:36px; font-weight:800; letter-spacing:2px;
  color:white; text-shadow: 0 0 10px #00e5ff, 0 0 30px #0a27a6;
  animation: float 3s ease-in-out infinite;
}
@keyframes float {0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)}}

.badge {
  text-align:center; color:#7dd3fc; font-size:11px; letter-spacing:3px;
  font-weight:700; border:1px solid #00e5ff33; background:#0a192f88;
  padding:6px 14px; border-radius:20px; display:inline-block; margin:8px auto;
  backdrop-filter: blur(10px);
}

/* CHAT */
div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}
.stChatMessage {background:transparent!important; border:none!important;}
div[data-testid="stChatMessageContent"] {padding:0!important;}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{
    background: linear-gradient(135deg, #0a27a6, #3a5bff)!important; color:white!important;
    border-radius:18px 18px 4px 18px!important; padding:12px 16px!important;
    max-width:80%; margin-left:auto; box-shadow: 0 0 20px #0a27a677!important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"]{
    background: rgba(30,41,59,0.8)!important; backdrop-filter: blur(12px)!important;
    color:#f1f5f9!important; border:1px solid #334155!important;
    border-radius:18px 18px 18px 4px!important; padding:12px 16px!important; max-width:80%;
}

/* INPUT */
div[data-testid="stBottom"] > div {background: rgba(11,16,32,0.8)!important; backdrop-filter: blur(20px)!important; border-top:1px solid #1e293b!important;}
input, textarea {background:#1e293b!important; color:white!important; border-radius:24px!important; border:1px solid #334155!important;}

/* BOUTONS CLASSES HIGH TECH */
div[data-testid="stButton"] > button {
    background: rgba(30,41,59,0.6)!important; backdrop-filter: blur(8px)!important;
    color:white!important; border:1px solid #334155!important; border-radius:12px!important;
    font-weight:700!important; height:48px!important; transition:0.2s!important;
}
div[data-testid="stButton"] > button:hover {
    background: #0a27a6!important; border-color:#00e5ff!important;
    box-shadow: 0 0 20px #00e5ff88!important; transform: translateY(-2px)!important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #0a27a6, #00e5ff)!important; color:white!important;
    border:none!important; box-shadow: 0 0 25px #00e5ff66!important;
}

/* EXPANDER */
div[data-testid="stExpander"] {background: rgba(17,26,51,0.8)!important; border:1px solid #1e3a8a!important; border-radius:16px!important;}
div[data-testid="stExpander"] summary {color:white!important; font-weight:700!important;}
div[data-testid="stExpander"] p {color:#cbd5e1!important;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if not KEY:
    st.error("Mets GROQ_API_KEY dans Secrets")
    st.stop()

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "classe" not in st.session_state:
    st.session_state.classe = "Master 1"

def ask(question, image=None):
    if image:
        b64 = base64.b64encode(image).decode()
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"[{st.session_state.classe}] {question}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }]
        }
    else:
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": f"Tu es Angel, prof pour niveau {st.session_state.classe}. Tu expliques simple et clair, adapté à ce niveau."},
                {"role": "user", "content": question}
            ]
        }

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json=payload,
        timeout=60
    ).json()

    return res["choices"][0]["message"]["content"]

# --- HEADER ULTRA HIGH-TECH ---
st.markdown("<div class='angel-title'>🕊️ ANGEL</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;'><span class='badge'>⚡ NEURAL ENGINE • {st.session_state.classe} • ONLINE</span></div>", unsafe_allow_html=True)

# SELECTION NIVEAUX
with st.expander(f"📚 Niveau actuel : {st.session_state.classe} — Changer"):
    st.markdown("<p style='color:#7dd3fc; font-size:11px; letter-spacing:2px; font-weight:700;'>COLLÈGE</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, c in enumerate(["6e","5e","4e","3e"]):
        with cols[i]:
            if st.button(c, key=f"classe_{c}", use_container_width=True, type="primary" if c == st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.rerun()
    st.markdown("<p style='color:#7dd3fc; font-size:11px; letter-spacing:2px; font-weight:700; margin-top:12px;'>LYCÉE</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, c in enumerate(["Seconde","Première","Terminale"]):
        with cols[i]:
            if st.button(c, key=f"classe_{c}", use_container_width=True, type="primary" if c == st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.rerun()
    st.markdown("<p style='color:#7dd3fc; font-size:11px; letter-spacing:2px; font-weight:700; margin-top:12px;'>UNIVERSITÉ</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, c in enumerate(["Licence 1","Licence 2","Licence 3"]):
        with cols[i]:
            if st.button(c, key=f"classe_{c}", use_container_width=True, type="primary" if c == st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.rerun()
    cols = st.columns(3)
    for i, c in enumerate(["Master 1","Master 2","Doctorat"]):
        with cols[i]:
            if st.button(c, key=f"classe_{c}", use_container_width=True, type="primary" if c == st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.rerun()

# Historique
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Photo
with st.expander("📷 Envoyer une photo"):
    photo = st.file_uploader("Choisis une image", type=["jpg","jpeg","png"])
    camera = st.camera_input("Prends une photo")
    img = None
    if camera:
        img = camera.getvalue()
    if photo:
        img = photo.getvalue()
    if img and st.button("⚡ Analyser avec Angel", type="primary"):
        reponse = ask("Explique cet exercice étape par étape", img)
        st.session_state.messages.append({"role": "user", "content": "📷 Photo envoyée"})
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        st.rerun()

# Chat
prompt = st.chat_input("Message à Angel...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    reponse = ask(prompt)

    st.session_state.messages.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
        st.write(reponse)

if st.button("🗑️ Effacer la conversation"):
    st.session_state.messages = []
    st.rerun()
