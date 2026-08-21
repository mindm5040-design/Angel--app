import streamlit as st
import requests, os, base64
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧬", layout="centered")

def get_key(name):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except: pass
    return os.getenv(name, "")

GROQ_KEY = get_key("GROQ_API_KEY")
ELEVEN_KEY = get_key("ELEVENLABS_API_KEY")

st.markdown("""
<style>
.stApp{background:#FCFCF9!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.angel-title{font-family:Space Grotesk;font-size:42px;font-weight:700;text-align:center;margin-top:14px;}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR MEMOIRE ---
with st.sidebar:
    st.title("🧬 Angel Mémoire")
    prenom = st.text_input("Ton prénom", value=st.session_state.get("prenom",""))
    niveau = st.selectbox("Ton niveau", ["Doctorat","Master","Licence","Bac"], index=0)
    st.session_state.prenom = prenom
    st.session_state.niveau = niveau
    st.divider()
    st.caption("Si tu as une clé ElevenLabs, mets-la dans Secrets pour avoir la voix naturelle d'Angel.")

if not GROQ_KEY:
    st.warning("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_groq(q, mode="cours"):
    system = f"Tu es Angel, prof bienveillante. Tu t'adresses à {prenom if prenom else 'l'étudiant'} qui est en {niveau}. Parle en français, clair, niveau {niveau}."
    if mode=="quiz":
        system += " Génère 3 QCM avec 4 propositions et la bonne réponse expliquée."
    data = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":system},{"role":"user","content":q}]}
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ_KEY}"}, json=data, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def speak_buttons(text, id):
    safe = text.replace("`","").replace("'","\\'").replace('"','\\"').replace("\n"," ")[:3500]
    components.html(f"""
    <div style="display:flex;gap:8px;margin-top:8px">
      <button onclick="speak_{id}()" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:6px 14px;font-size:13px;cursor:pointer">🔊 Faire lire par Angel</button>
      <button onclick="quiz_{id}()" style="background:white;color:#E07A4F;border:1px solid #E07A4F;border-radius:20px;padding:6px 14px;font-size:13px;cursor:pointer">🧠 Teste-moi</button>
    </div>
    <script>
    function speak_{id}(){{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang='fr-FR'; u.rate=0.95; window.speechSynthesis.speak(u);
    }}
    function quiz_{id}(){{
        window.parent.postMessage({{type:'quiz', id:{id}}}, '*');
    }}
    </script>
    """, height=50)

st.markdown(f'<div style="text-align:center;margin:20px 0"><div style="font-size:70px">🧬</div><div class="angel-title">Angel AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700">DNA REPLICATION - ACTIVE</div><div style="margin-top:8px">Salut {prenom if prenom else ""} 👋 Niveau {niveau}</div></div>', unsafe_allow_html=True)

for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"]=="assistant":
            speak_buttons(m["content"], i)

prompt = st.chat_input("Pose ta question à Angel...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    box = st.empty()
    box.markdown('<div style="background:white;padding:12px 18px;border-radius:20px;border:1px solid #eee">🧬 Angel réplique son ADN...</div>')
    ans = ask_groq(prompt, "cours")
    box.empty()
    st.session_state.messages.append({"role":"assistant","content":ans})
    with st.chat_message("assistant"):
        st.markdown(ans)
        speak_buttons(ans, len(st.session_state.messages))

# bouton quiz global
if st.session_state.messages and st.session_state.messages[-1]["role"]=="assistant":
    if st.button("🧠 Générer un quiz sur le dernier cours"):
        last_cours = st.session_state.messages[-1]["content"]
        q = ask_groq(f"Fais un quiz sur ce cours: {last_cours}", "quiz")
        st.session_state.messages.append({"role":"assistant","content": "### 🧠 Quiz Angel\n"+q})
        st.rerun()
