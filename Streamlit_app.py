import streamlit as st
import requests, os, base64
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
    return '<div style="width:150px;height:150px;border-radius:50%;background:white;border:3px solid #E07A4F;display:flex;align-items:center;justify-content:center;position:relative;"><div style="font-size:70px;animation:dnaMove 2.8s ease-in-out infinite;">🧬</div><div style="position:absolute;inset:-6px;border-radius:50%;border:2px dashed rgba(224,122,79,0.35);animation:spin 5s linear infinite;"></div></div>'

def speak_button(text, key_id):
    safe = text.replace("`","").replace("'"," ").replace('"'," ").replace("\n"," ")[:3500]
    components.html(f"""
    <div>
      <button onclick="speak_{key_id}()" id="btn_{key_id}" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:7px 16px;font-size:13px;cursor:pointer;margin-top:8px;">🔊 Faire lire par Angel - 🔊 Read by Angel</button>
      <select id="lang_{key_id}" style="margin-left:8px;border-radius:12px;padding:5px;border:1px solid #ddd;">
        <option value="auto">Auto 🌍</option>
        <option value="fr-FR">Français</option>
        <option value="en-US">English</option>
        <option value="de-DE">Deutsch</option>
        <option value="es-ES">Español</option>
        <option value="it-IT">Italiano</option>
        <option value="pt-PT">Português</option>
        <option value="ar-SA">العربية</option>
      </select>
    </div>
    <script>
    function speak_{key_id}(){{
        window.speechSynthesis.cancel();
        var txt = `{safe}`;
        var sel = document.getElementById('lang_{key_id}').value;
        var u = new SpeechSynthesisUtterance(txt);
        if(sel=='auto'){{
            if(/[àâéèêëîïôùûüÿç]/i.test(txt) || txt.toLowerCase().includes('bonjour')) u.lang='fr-FR';
            else if(txt.toLowerCase().includes('hallo') || txt.includes('ß')) u.lang='de-DE';
            else if(txt.toLowerCase().includes('hola')) u.lang='es-ES';
            else u.lang='en-US';
        }} else {{ u.lang=sel; }}
        u.rate=0.95;
        var voices = window.speechSynthesis.getVoices();
        var fem = voices.find(v=>v.lang.includes(u.lang.substring(0,2)) && v.name.toLowerCase().includes('female')) || voices.find(v=>v.lang==u.lang);
        if(fem) u.voice=fem;
        window.speechSynthesis.speak(u);
    }}
    </script>
    """, height=60)

st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;margin:20px 0;"><div>{get_logo()}</div><div class="angel-title">Angel AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;margin-top:6px;">POLYGLOT • ALL LANGUAGES</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute ta cle GROQ")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]

def ask_groq(q):
    try:
        data={{"model":"openai/gpt-oss-20b","messages":[{{"role":"system","content":"Tu es Angel, prof polyglotte. Tu reponds dans la langue de l'utilisateur. Si on te parle en anglais tu reponds en anglais, en allemand en allemand, etc. Toujours bienveillante."}},{{"role":"user","content":q}}]}}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={{"Authorization":f"Bearer {{KEY}}"}},json=data,timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {{e}}"

for i,m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"]=="assistant":
            speak_button(m["content"], i)

prompt=st.chat_input("Pose ta question dans ta langue...")
if prompt:
    st.session_state.messages.append({{"role":"user","content":prompt}})
    with st.chat_message("user"):
        st.markdown(prompt)
    box=st.empty()
    box.markdown('<div style="background:white;padding:12px 18px;border-radius:20px;border:1px solid #eee;">🧬 Angel traduit et replique...</div>', unsafe_allow_html=True)
    ans=ask_groq(prompt)
    box.empty()
    st.session_state.messages.append({{"role":"assistant","content":ans}})
    with st.chat_message("assistant"):
        st.markdown(ans)
        speak_button(ans, len(st.session_state.messages))
