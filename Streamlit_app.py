import streamlit as st
import requests, os, random, urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI ⚡", page_icon="⚡", layout="centered")

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
.stApp{background:#0F0F1A!important;color:white!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.nexa-title{font-size:42px;font-weight:800;text-align:center;background: linear-gradient(90deg, #7F5AF0, #2CB67D);-webkit-background-clip: text;-webkit-text-fill-color: transparent;}
.mode-card{background:#1F1F2E;border:1px solid #2CB67D;border-radius:16px;padding:12px;margin:8px 0;}
.stButton>button{background:#7F5AF0;color:white;border-radius:20px;}
</style>""", unsafe_allow_html=True)

def ask_groq(prompt):
    if not KEY: return "⚠️ Ajoute GROQ_API_KEY dans Secrets"
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":"Bearer "+KEY},
        json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":prompt}]},
        timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "😅 NEXA se reconnecte... Réessaie dans 2s"

def speak_btn(txt,kid):
    safe=txt.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:1500]
    h="<button onclick='s%s()' style='background:#2CB67D;color:white;border:none;border-radius:20px;padding:6px 14px;'>🔊 Ecouter</button><script>function s%s(){window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(`%s`);u.lang='fr-FR';u.rate=1.0;window.speechSynthesis.speak(u);}</script>" % (kid,kid,safe)
    components.html(h,height=45)

# HEADER + BOUTON PROFIL
col1, col2 = st.columns([4,1])
with col1:
    st.markdown('<div style="text-align:center"><div style="font-size:60px;">⚡</div><div class="nexa-title">NEXA-AI</div><div style
