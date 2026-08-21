import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

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

st.title("🕊️ Angel")
st.caption(f"Niveau actuel : {st.session_state.classe} • {len(st.session_state.messages)} messages")

# SELECTION NIVEAU
with st.expander(f"📚 Changer de niveau : {st.session_state.classe}"):
    cols = st.columns(4)
    for i, c in enumerate(CLASSES):
        with cols[i % 4]:
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
    if img and st.button("Analyser", type="primary"):
        reponse = ask("Explique cet exercice étape par étape", img)
        st.session_state.messages.append({"role": "user", "content": "📷 Photo envoyée"})
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        st.rerun()

# Chat
prompt = st.chat_input("Message")

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
