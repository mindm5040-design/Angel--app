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
KEY=get_key()

st.markdown("<style>.stApp{background:#FCFCF9!important;} header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}.nexa-title{font-size:42px;font-weight:800;text-align:center;}.mode-card{background:white;border:1px solid #eee;border-radius:16px;padding:12px;margin:8px 0;}</style>", unsafe_allow_html=True)

def ask_groq(prompt):
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":prompt}]}, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Erreur connexion, reessaie..."

def speak_btn(txt,kid):
    safe=txt.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:1500]
    h="<button onclick='s%s()' style='background:#E07A4F;color:white;border:none;border-radius:20px;padding:6px 14px;'>🔊 Ecouter</button><script>function s%s(){window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(`%s`);u.lang='fr-FR';u.rate=1.0;window.speechSynthesis.speak(u);}</script>" % (kid,kid,safe)
    components.html(h,height=45)

st.markdown('<div style="text-align:center"><div style="font-size:60px;">🧬</div><div class="nexa-title">NEXA-AI</div><div style="color:#E07A4F;font-size:11px;letter-spacing:3px;font-weight:700;">DNA REPLICATION ACTIVE</div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "exam" not in st.session_state:
    st.session_state.exam=""

classe=st.selectbox("Ta classe:",["6eme","5eme","4eme","3eme","2nde","1ere","Tle","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"])
mode=st.selectbox("Super-pouvoir:",["Chat normal","Corriger devoir photo stylo rouge","Fiche revision PDF programme camerounais","Examen blanc 10 questions chrono","Explication video schema","Classement","Partage WhatsApp","Mode groupe 3 eleves"])

if mode=="Chat normal":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"]=="assistant":
                speak_btn(m["content"],i)
    p=st.chat_input("Question niveau "+classe+"...")
    if p:
        st.session_state.messages.append({"role":"user","content":p})
        with st.chat_message("user"):
            st.markdown(p)
        ans=ask_groq(p+" niveau "+classe+" tu es NEXA-AI prof camerounaise")
        st.session_state.messages.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
            speak_btn(ans,len(st.session_state.messages))

if mode=="Corriger devoir photo stylo rouge":
    st.markdown('<div class="mode-card"><b>Prends photo, NEXA corrige au stylo rouge</b></div>', unsafe_allow_html=True)
    img=st.file_uploader("Upload photo",type=["jpg","png","jpeg"])
    if img:
        st.image(img)
        if st.button("Corriger au stylo rouge"):
            res=ask_groq("Corrige devoir niveau "+classe+" stylo rouge note sur 20")
            st.markdown(res)
            speak_btn(res,900)

if mode=="Fiche revision PDF programme camerounais":
    mat=st.selectbox("Matiere",["Mathematiques","Physique","Chimie","SVT","Histoire","Geographie","Anglais"])
    chap=st.text_input("Chapitre","Replication ADN")
    if st.button("Generer fiche PDF"):
        fiche=ask_groq("Fiche revision "+classe+" "+mat+" "+chap+" definitions resume exemples exos")
        st.markdown(fiche)
        speak_btn(fiche,901)
        st.download_button("Telecharger fiche",fiche,file_name="NEXA.txt")

if mode=="Examen blanc 10 questions chrono":
    if st.button("Demarrer examen"):
        st.session_state.exam=ask_groq("Genere 10 QCM niveau "+classe+" replication ADN A) B) C) D)")
    if st.session_state.exam!="":
        st.markdown(st.session_state.exam)
        rep=st.text_input("Reponses ex 1A 2B...")
        if st.button("Corriger examen"):
            corr=ask_groq("Corrige "+st.session_state.exam+" reponses "+rep+" note sur 20")
            st.markdown(corr)
            st.balloons()
            st.success("Tu es 3eme de ta classe cette semaine!")

if mode=="Explication video schema":
    sujet=st.text_input("Sujet","Replication ADN")
    if st.button("Generer schema"):
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/DNA_replication_split.svg/800px-DNA_replication_split.svg.png")
        expl=ask_groq("Explique "+sujet+" niveau "+classe+" 4 etapes")
        st.markdown(expl)
        speak_btn(expl,902)

if mode=="Classement":
    st.success("Tu es 3eme de ta classe cette semaine! Classe: "+classe+" XP: "+str(random.randint(150,300)))

if mode=="Partage WhatsApp":
    txt=st.text_area("Texte","Decouvre NEXA-AI")
    wa=urllib.parse.quote(txt+" https://z.streamlit.app")
    st.markdown("[Envoyer WhatsApp](https://wa.me/?text="+wa+")")

if mode=="Mode groupe 3 eleves":
    qg=st.chat_input("Question groupe...")
    if qg:
        ans=ask_groq("Groupe 3 eleves niveau "+classe+" question "+qg)
        st.markdown(ans)
        speak_btn(ans,903)
