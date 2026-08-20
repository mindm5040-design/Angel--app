import streamlit as st
import requests, os, base64, random, urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI", page_icon="🧬", layout="centered")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY","")

KEY = get_key()

st.markdown("""
<style>
.stApp{background:#FCFCF9!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.nexa-title{font-size:42px;font-weight:800;text-align:center;margin-top:8px;}
.mode-card{background:white;border:1px solid #eee;border-radius:16px;padding:12px;margin:8px 0;}
</style>
""", unsafe_allow_html=True)

def ask_groq(prompt, system="Tu es NEXA-AI, prof camerounaise."):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":system},{"role":"user","content":prompt}]}, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def speak_btn(text, kid):
    safe = text.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:2000]
    html = """
    <button onclick="speak_%s()" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:6px 14px;font-size:12px;">🔊 Ecouter NEXA</button>
    <select id="lang_%s" style="margin-left:6px;border-radius:10px;padding:3px;">
        <option value="fr-FR">FR</option>
        <option value="en-US">EN</option>
        <option value="de-DE">DE</option>
        <option value="es-ES">ES</option>
    </select>
    <script>
    function speak_%s(){
        window.speechSynthesis.cancel();
        var t = `%s`;
        var l = document.getElementById('lang_%s').value;
        var u = new SpeechSynthesisUtterance(t);
        u.lang = l; u.rate=0.95;
        window.speechSynthesis.speak(u);
    }
    </script>
    """ % (kid, kid, kid, safe, kid)
    components.html(html, height=50)

st.markdown('<div style="text-align:center"><div style="font-size:60px;">🧬</div><div class="nexa-title">NEXA-AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;">POLYGLOT CAMEROUN</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]

classe = st.selectbox("Ta classe:", ["6eme","5eme","4eme","3eme","2nde","1ere","Tle","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"])
mode = st.selectbox("Super-pouvoir:", ["Chat normal","Corriger devoir photo stylo rouge","Fiche revision PDF programme camerounais","Examen blanc 10 questions chrono","Explication video schema","Classement","Partage WhatsApp","Mode groupe 3 eleves"])

if mode == "Chat normal":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"]=="assistant":
                speak_btn(m["content"], i)
    p = st.chat_input("Question niveau "+classe+"...")
    if p:
        st.session_state.messages.append({"role":"user","content":p})
        with st.chat_message("user"):
            st.markdown(p)
        with st.spinner("NEXA replique..."):
            ans = ask_groq(p, "Tu es NEXA-AI niveau "+classe+", prof camerounaise polyglotte")
        st.session_state.messages.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
            speak_btn(ans, len(st.session_state.messages))

if mode == "Corriger devoir photo stylo rouge":
    st.markdown('<div class="mode-card"><b>Prends photo, NEXA corrige au stylo rouge</b></div>', unsafe_allow_html=True)
    img = st.file_uploader("Upload photo devoir", type=["jpg","jpeg","png"])
    if img:
        st.image(img)
        if st.button("Corriger au stylo rouge"):
            with st.spinner("Correction..."):
                b64 = base64.b64encode(img.getvalue()).decode()
                try:
                    payload = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":"Corrige devoir "+classe+" stylo rouge note sur 20"},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
                    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json=payload, timeout=90).json()
                    res = r["choices"][0]["message"]["content"]
                except:
                    res = ask_groq("Corrige devoir niveau "+classe+" stylo rouge note sur 20")
                st.markdown("### Correction")
                st.markdown(res)
                speak_btn(res, 900)

if mode == "Fiche revision PDF programme camerounais":
    st.markdown('<div class="mode-card"><b>Fiches revisions PDF programme camerounais</b></div>', unsafe_allow_html=True)
    mat = st.selectbox("Matiere", ["Mathematiques","Physique","Chimie","SVT","Histoire","Geographie","Anglais","Philosophie","Informatique"])
    chap = st.text_input("Chapitre", "Replication ADN")
    if st.button("Generer fiche PDF"):
        with st.spinner("Generation..."):
            fiche = ask_groq("Fiche revision "+classe+" "+mat+" "+chap+" def resume exemples exos corriges")
            st.markdown(fiche)
            speak_btn(fiche, 901)
            wa = urllib.parse.quote("Fiche NEXA-AI "+mat+" "+chap+" "+fiche[:500])
            st.markdown("[Partager WhatsApp 1 clic](https://wa.me/?text="+wa+")")
            st.download_button("Telecharger fiche", fiche, file_name="NEXA.txt")

if mode == "Examen blanc 10 questions chrono":
    st.markdown('<div class="mode-card"><b>Mode examen blanc: 10 questions chronometrees</b></div>', unsafe_allow_html=True)
    if st.button("Demarrer examen"):
        qs = ask_groq("Genere 10 QCM niveau "+classe+" replication ADN format Q1 A) B) C) D) sans reponses")
        st.session_state["exam"]=qs
    if "exam" in st.session_state:
        st.markdown(st.session_state["exam"])
        rep = st.text_input("Reponses ex: 1A 2B...")
        if st.button("Corriger examen"):
            corr = ask_groq("Corrige: "+st.session_state["exam"]+" Reponses: "+rep+" note sur 20")
            st.markdown(corr)
            st.balloons()
            st.success("Tu es 3eme de ta classe cette semaine!")

if mode == "Explication video schema":
    st.markdown('<div class="mode-card"><b>Explication video: NEXA genere schema</b></div>', unsafe_allow_html=True)
    sujet = st.text_input("Sujet", "Replication ADN")
    if st.button("Generer schema"):
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/DNA_replication_split.svg/800px-DNA_replication_split.svg.png")
        expl = ask_groq("Explique "+sujet+" niveau
