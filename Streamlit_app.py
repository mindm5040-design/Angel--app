import streamlit as st
import requests, os, base64, random, time, urllib.parse
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI", page_icon="🧬", layout="centered")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY","")
KEY=get_key()

st.markdown("""
<style>
.stApp{background:#FCFCF9!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.nexa-title{font-size:42px;font-weight:800;text-align:center;margin-top:10px;}
.mode-card{background:white;border:1px solid #eee;border-radius:16px;padding:12px 14px;margin:6px 0;box-shadow:0 2px 8px rgba(0,0,0,0.04);}
@keyframes dnaMove{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
</style>
""", unsafe_allow_html=True)

def get_logo():
    return '<div style="width:130px;height:130px;border-radius:50%;background:white;border:3px solid #E07A4F;display:flex;align-items:center;justify-content:center;position:relative;margin:auto;"><div style="font-size:60px;animation:dnaMove 3s linear infinite;">🧬</div><div style="position:absolute;inset:-6px;border-radius:50%;border:2px dashed rgba(224,122,79,0.35);animation:spin 5s linear infinite;"></div></div>'

def ask_groq(prompt, system="Tu es NEXA-AI, prof camerounaise polyglotte."):
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":system},{"role":"user","content":prompt}]}, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur Groq: {e}"

def speak_html(text, kid):
    safe=text.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:2500]
    html="""<button onclick="speak_%s()" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:6px 14px;font-size:12px;">🔊 Ecouter</button><script>function speak_%s(){window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(`%s`);u.lang='fr-FR';u.rate=0.95;window.speechSynthesis.speak(u);}</script>"""%(kid,kid,safe)
    components.html(html,height=40)

st.markdown(f'<div style="text-align:center;margin:10px 0 5px 0;">{get_logo()}<div class="nexa-title">NEXA-AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;">POLYGLOT • SUPER-POUVOIRS ACTIVES</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

# --- MENU MODES ---
mode = st.selectbox("Choisis ton super-pouvoir NEXA:", ["💬 Chat normal","📸 Corriger devoir en photo (stylo rouge)","📄 Fiche de revision PDF - Programme camerounais","⏱️ Mode examen blanc - 10 questions chrono","
