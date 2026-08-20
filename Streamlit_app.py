import streamlit as st
import requests, base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI v4.0", page_icon="🕊️", layout="centered")

# --- DESIGN HIGH TECH ---
st.markdown("""
<style>
.stApp {background:#020617!important;}
header, footer, #MainMenu {visibility:hidden!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}

.stChatMessage {border:none!important; background:transparent!important;}
div[data-testid="stChatMessageContent"] {padding:0!important;}

/* BUBBLES NEON */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{
    background:linear-gradient(135deg, #0a27a6, #00e5ff)!important; color:white!important;
    border:1px solid #00e5ff88!important; border-radius:18px 18px 4px 18px!important;
    padding:10px 14px!important; max-width:80%; margin-left:auto; box-shadow:0 0 15px #00e5ff44!important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"]{
    background:#0a192fcc!important; color:#7dd3fc!important; border:1px solid #00e5ff33!important;
    border-radius:18px 18px 18px 4px!important; padding:10px 14px!important; max-width:80%;
}

div[data-testid="stBottom"] > div {background:#020617!important; border-top:1px solid #00e5ff33!important;}
input, textarea{background:#0a192f!important; border:1px solid #00e5ff33!important; color:#00e5ff!important; border-radius:20px!important;}

div[data-testid="stButton"] > button {background:#0a192f!important; color:#00e5ff!important; border:1px solid #00e5ff44!important; border-radius:12px!important; font-weight:700!important;}
div[data-testid="stButton"] > button:hover {background:#00e5ff!important; color:#020617!important; box-shadow:0 0 20px #00e5ff!important;}
button[kind="primary"] {background:linear-gradient(90deg,#0a27a6,#00e5ff)!important; color:white!important; border:none!important; box-shadow:0 0 20px #00e5ff88!important;}
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
                {"role": "system", "content": f"Tu es Angel IA Cameroun v4.0, prof pour niveau {st.session_state.classe}. Tu expliques simple et clair, adapté à ce niveau."},
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

# --- HOLOGRAMME EN HAUT COMME SUR TON IMAGE ---
components.html("""
<div style="position:relative; width:100%; height:260px; background: radial-gradient(ellipse at center, #0a2540 0%, #020617 70%); border:1px solid #00e5ff33; border-radius:18px; overflow:hidden; font-family:monospace;">
<div style="position:absolute; width:100%; height:2px; background:linear-gradient(90deg,transparent,#00e5ff,transparent); animation: scan 2.5s linear infinite; z-index:10;"></div>
<style>@keyframes scan{0%{top:0}100%{top:100%}} @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.3)}} @keyframes draw{to{stroke-dashoffset:0;}}</style>
<div style="position:absolute; top:12px; left:14px; color:#00e5ff; font-size:11px; font-weight:800; letter-spacing:2px; text-shadow:0 0 8px #00e5ff;">IA CAMEROUN v4.0 • ANGEL AI • SYSTEM ONLINE • SYNC 100%</div>
<div style="position:absolute; left:50%; top:50%; transform:translate(-50%,-40%);">
<svg width="160" height="190" viewBox="0 0 100 140"><path d="M 35 2 L 55 5 L 62 18 L 68 22 L 72 35 L 70 48 L 65 58 L 68 70 L 70 85 L 68 100 L 65 115 L 60 125 L 45 128 L 30 124 L 25 110 L 20 95 L 18 80 L 15 65 L 18 50 L 22 35 L 28 15 Z" fill="none" stroke="#00e5ff" stroke-width="1.3" stroke-dasharray="1000" stroke-dashoffset="1000" style="animation: draw 3s ease forwards; filter:drop-shadow(0 0 10px #00e5ff);"/></svg>
<div style="position:absolute; left:48%; top:82%; width:8px; height:8px; background:#00e5ff; border-radius:50%; box-shadow:0 0 10px #00e5ff; animation: pulse 1.5s infinite;"></div>
<div style="position:absolute; left:20%; top:68%; width:8px; height:8px; background:#00e5ff; border-radius:50%; box-shadow:0 0 10px #00e5ff; animation: pulse 1.5s infinite;"></div>
</div>
<div style="position:absolute; bottom:10px; width:100%; text-align:center; color:#7dd3fc; font-size:9px; letter-spacing:1px;">YAOUNDÉ • DOUALA • BAMENDA • RÉSEAU NEURAL ACTIF • LATENCY 12ms</div>
</div>
""", height=280)

st.markdown(f"<div style='text-align:center; color:#00e5ff; font-family:monospace; font-size:12px; letter-spacing:2px; margin:10px 0;'>🕊️ ANGEL • NIVEAU : {st.session_state.classe} • {len(st.session_state.messages)} MESSAGES</div>", unsafe_allow_html=True)

# SELECTION NIVEAUX HIGH TECH
with st.expander(f"📚 Changer de niveau : {st.session_state.classe}"):
    st.markdown("<div style='color:#00e5ff; font-size:10px; font-family:monospace; letter-spacing:2px;'>COLLÈGE</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, c in enumerate(["6e","5e","4e","3e"]):
        with cols[i]:
            if st.button(c, key=f"classe_{c}", use_container_width=True, type="primary" if c == st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.rerun()
    st.markdown("<div style='color:#00e5ff; font-size:10px; font-family:monospace; letter-spacing:2px; margin-top:10px;'>LYCÉE</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, c in enumerate(["Seconde","Première","Terminale"]):
        with cols[i]:
            if st.button(c, key=f"classe_{c}", use_container_width=True, type="primary" if c == st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.rerun()
    st.markdown("<div style='color:#00e5ff; font-size:10px; font-family:monospace; letter-spacing:2px; margin-top:10px;'>UNIVERSITÉ</div>", unsafe_allow_html=True)
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
    photo = st.file_uploader("Choisis", type=["jpg","jpeg","png"])
    camera = st.camera_input("Prends une photo")
    img = None
    if camera:
        img = camera.getvalue()
    if photo:
        img = photo.getvalue()
    if img and st.button("Analyser ⚡", type="primary"):
        reponse = ask("Explique cet exercice étape par étape", img)
        st.session_state.messages.append({"role": "user", "content": "📷 Photo envoyée"})
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        st.rerun()

# Chat
prompt = st.chat_input("Message à Angel IA v4.0...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    reponse = ask(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
        st.write(reponse)

if st.button("🗑️ Effacer"):
    st.session_state.messages = []
    st.rerun()
