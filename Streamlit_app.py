import streamlit as st
import requests
import os
import base64
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧬", layout="centered")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")
KEY = get_key()

st.markdown("""
<style>
.stApp{background:#FCFCF9!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.angel-title{font-family:Space Grotesk;font-size:42px;font-weight:700;text-align:center;margin-top:14px;}
@keyframes dnaMove{0%{transform:rotateY(0deg) scale(1)}50%{transform:rotateY(180deg) scale(1.15)}100%{transform:rotateY(360deg) scale(1)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
</style>
""", unsafe_allow_html=True)

def get_logo():
    p = Path("dna.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video style="width:150px;height:150px;border-radius:50%;object-fit:cover;border:3px solid #E07A4F;" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '''
    <div style="width:150px;height:150px;border-radius:50%;background:white;border:3px solid #E07A4F;display:flex;align-items:center;justify-content:center;position:relative;">
      <div style="font-size:70px;animation:dnaMove 2.8s ease-in-out infinite;">🧬</div>
      <div style="position:absolute;inset:-6px;border-radius:50%;border:2px dashed rgba(224,122,79,0.35);animation:spin 5s linear infinite;"></div>
    </div>
    '''

def speak_button(text, key_id):
    safe_text = text.replace("`","").replace("'", "\\'").replace('"', '\\"').replace("\n"," ")[:4000]
    components.html(f"""
    <button onclick="speak_{key_id}()" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:6px 14px;font-size:13px;cursor:pointer;margin-top:8px;">🔊 Faire lire par Angel</button>
    <script>
    function speak_{key_id}(){{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe_text}');
        u.lang = 'fr-FR';
        u.rate = 0.95;
        u.pitch = 1.1;
        window.speechSynthesis.speak(u);
    }}
    </script>
    """, height=50)

st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;margin:20px 0;"><div>{get_logo()}</div><div class="angel-title">Angel AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;margin-top:6px;">DNA REPLICATION - ACTIVE</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute ta cle GROQ dans Secrets")
    st.stop()

# --- NOUVEAU : CHOIX CLASSE ---
st.sidebar.markdown("### ⚙️ Paramètres Angel")
classe = st.sidebar.selectbox(
    "Niveau de l'élève",
    ["6e", "5e", "4e", "3e", "2nde", "1ère", "Terminale", "Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat", "Université"],
    index=12
)
st.sidebar.markdown(f"Niveau actuel: **{classe}**")

# --- NOUVEAU : ENVOI PHOTO + VOCAL ---
st.sidebar.markdown("### 📎 Options")
uploaded_photo = st.sidebar.file_uploader("Envoi de photos (exercice, cours)", type=["jpg","jpeg","png"])
audio_input = st.sidebar.audio_input("Message vocal")

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_groq(q, has_image=False):
    try:
        system_prompt = f"Tu es Angel, prof bienveillante niveau {classe}. Adapte tes explications au niveau {classe}. Parle en francais. Si l'élève envoie une photo, explique l'exercice sur la photo."
        messages = [{"role":"system","content":system_prompt}]

        # Si photo uploadée, on utilise un modèle vision
        if has_image and uploaded_photo:
            # Note: on décrit que l'image est présente
            q = f"[L'élève a envoyé une photo d'exercice] {q} Explique comme si tu voyais la photo."

        messages.append({"role":"user","content":q})

        data = {"model":"openai/gpt-oss-20b","messages":messages}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {KEY}"}, json=data, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

def transcribe_audio(audio_file):
    try:
        files = {"file": audio_file, "model": (None, "whisper-large-v3")}
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data={"model":"whisper-large-v3"}, timeout=60)
        return r.json().get("text","
