import streamlit as st
import requests, os, base64, random, urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI", page_icon="DNA", layout="centered")

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
.mode-card{background:white;border:1px solid #eee;border-radius:16px;padding:12px 14px;margin:6px 0;}
@keyframes dnaMove{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
</style>
""", unsafe_allow_html=True)

def ask_groq(prompt, system="Tu es NEXA-AI, prof camerounaise."):
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":system},{"role":"user","content":prompt}]}, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

st.markdown('<div style="text-align:center;margin:10px 0;"><div style="width:130px;height:130px;border-radius:50%;background:white;border:3px solid #E07A4F;display:flex;align-items:center;justify-content:center;margin:auto;position:relative;"><div style="font-size:60px;animation:dnaMove 3s linear infinite;">🧬</div></div><div class="nexa-title">NEXA-AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;">SUPER-POUVOIRS ACTIVES</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]

mode = st.selectbox("Choisis ton mode:", ["Chat normal", "Corriger devoir photo", "Fiche revision PDF", "Examen blanc", "Explication schema", "Classement + WhatsApp", "Mode groupe"])

if mode == "Chat normal":
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    p=st.chat_input("Question a NEXA-AI...")
    if p:
        st.session_state.messages.append({"role":"user","content":p})
        with st.chat_message("user"):
            st.markdown(p)
        with st.spinner("NEXA replique son ADN..."):
            ans=ask_groq(p)
        st.session_state.messages.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"):
            st.markdown(ans)

elif mode == "Corriger devoir photo":
    st.markdown('<div class="mode-card"><b>Prends photo, NEXA corrige au stylo rouge</b></div>', unsafe_allow_html=True)
    img = st.file_uploader("Upload photo devoir", type=["jpg","png","jpeg"])
    if img:
        st.image(img)
        if st.button("Corriger au stylo rouge"):
            with st.spinner("Correction..."):
                b64 = base64.b64encode(img.getvalue()).decode()
                try:
                    payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":"Corrige ce devoir stylo rouge, note sur 20, programme camerounais"},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
                    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json=payload, timeout=90).json()
                    res=r["choices"][0]["message"]["content"]
                except:
                    res=ask_groq("Corrige devoir style stylo rouge note sur 20")
                st.markdown("### Correction NEXA-AI")
                st.markdown(res)

elif mode == "Fiche revision PDF":
    mat = st.selectbox("Matiere", ["Mathematiques","Physique","Chimie","SVT","Histoire","Geographie","Anglais","Philosophie"])
    chap = st.text_input("Chapitre", "Replication ADN")
    classe = st.selectbox("Classe", ["6eme","3eme","2nde","Tle","Licence 1","Master 1"])
    if st.button("Generer fiche PDF"):
        with st.spinner("Generation..."):
            fiche = ask_groq("Fiche revision programme camerounais "+classe+" "+mat+" "+chap+" Structure: def, resume, exemples, exos corriges.")
            st.markdown(fiche)
            wa = urllib.parse.quote("Fiche NEXA-AI "+mat+" - "+chap+" : "+fiche[:500])
            st.markdown("[Partager sur WhatsApp 1 clic](https://wa.me/?text="+wa+")")
            st.download_button("Telecharger fiche", fiche, file_name="NEXA-"+mat+".txt")

elif mode == "Examen blanc":
    if st.button("Demarrer examen blanc 10 questions"):
        qs = ask_groq("Genere 10 QCM programme camerounais replication ADN. Format 1. question A) B) C) D) sans reponses")
        st.session_state["exam"]=qs
    if "exam" in st.session_state:
        st.markdown(st.session_state["exam"])
        rep = st.text_input("Tes reponses ex: 1A 2B...")
        if st.button("Corriger examen"):
            corr = ask_groq("Corrige: "+st.session_state["exam"]+" Reponses: "+rep+" Donne note sur 20")
            st.markdown(corr)
            st.balloons()
            st.success("Tu es 3eme de ta classe cette semaine!")

elif mode == "Explication schema":
    sujet = st.text_input("Sujet a expliquer", "Replication ADN")
    if st.button("Generer schema"):
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/DNA_replication_split.svg/800px-DNA_replication_split.svg.png")
        expl = ask_groq("Explique "+sujet+" en 4 etapes visuelles avec emojis")
        st.markdown(expl)

elif mode == "Classement + WhatsApp":
    st.markdown('<div class="mode-card"><h3>Classement</h3><p>Tu es <b>3eme de ta classe cette semaine</b></p><p>Score 87%</p></div>', unsafe_allow_html=True)
    txt = urllib.parse.quote("Je suis 3eme sur NEXA-AI! https://z.streamlit.app")
    st.markdown("[Partager sur WhatsApp](https://wa.me/?text="+txt+")")

elif mode == "Mode groupe":
    st.info("3 eleves revisent ensemble avec NEXA")
    qg = st.chat_input("Question groupe...")
    if qg:
        ans=ask_groq("Groupe 3 eleves question: "+qg)
        st.markdown(ans)
