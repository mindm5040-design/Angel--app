import streamlit as st
import requests
import os
import base64
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI", page_icon="🧬", layout="centered")

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
.nexa-title{font-family:Space Grotesk;font-size:44px;font-weight:700;text-align:center;margin-top:14px;letter-spacing:-1px;}
@keyframes dnaMove{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
</style>
""", unsafe_allow_html=True)

def get_logo():
    p = Path("dna.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video style="width:150px;height:150px;border-radius:50%;object-fit:cover;border:3px solid #E07A4F;" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '<div style="width:150px;height:150px;border-radius:50%;background:white;border:3px solid #E07A4F;display:flex;align-items:center;justify-content:center;position:relative;"><div style="font-size:70px;animation:dnaMove 3s linear infinite;">🧬</div><div style="position:absolute;inset:-6px;border-radius:50%;border:2px dashed rgba(224,122,79,0.35);animation:spin 5s linear infinite;"></div></div>'

def speak_button(text, kid):
    safe = text.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:3000]
    html = """
    <div>
      <button onclick="speak_%s()" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:7px 16px;font-size:13px;cursor:pointer;">🔊 Ecouter NEXA</button>
      <select id="lang_%s" style="margin-left:8px;border-radius:12px;padding:4px;border:1px solid #ddd;">
        <option value="auto">Auto 🌍</option>
        <option value="fr-FR">Francais</option>
        <option value="en-US">English</option>
        <option value="de-DE">Deutsch</option>
        <option value="es-ES">Espanol</option>
      </select>
    </div>
    <script>
    function speak_%s(){
        window.speechSynthesis.cancel();
        var txt = `%s`;
        var sel = document.getElementById('lang_%s').value;
        var u = new SpeechSynthesisUtterance(txt);
        if(sel=='auto'){
            if(txt.toLowerCase().includes('hallo')) u.lang='de-DE';
            else if(txt.toLowerCase().includes('hola')) u.lang='es-ES';
            else if(/[àâéèêëîïôùûüÿç]/i.test(txt)) u.lang='fr-FR';
            else u.lang='en-US';
        } else { u.lang=sel; }
        u.rate=0.95;
        window.speechSynthesis.speak(u);
    }
    </script>
    """ % (kid, kid, kid, safe, kid)
    components.html(html, height=60)

st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;margin:20px 0;"><div>{get_logo()}</div><div class="nexa-title">NEXA-AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;margin-top:6px;">POLYGLOT • ALL LANGUAGES</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute ta cle GROQ dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_groq(q):
    try:
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "Tu es NEXA-AI, intelligence artificielle polyglotte avancee. Tu t'appelles NEXA-AI, plus Angel. Tu reponds dans la langue de l'utilisateur, tres bienveillante, claire, niveau Doctorat."},
                {"role": "user", "content": q}
            ]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": "Bearer " + KEY}, json=payload, timeout=60)
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            speak_button(m["content"], i)

prompt = st.chat_input("Pose ta question a NEXA-AI...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("🧬 NEXA-AI replique son ADN..."):
        ans = ask_groq(prompt)

    st.session_state.messages.append({"role": "assistant", "content": ans})
    with st.chat_message("assistant"):
        st.markdown(ans)
        speak_button(ans, len(st.session_state.messages))
