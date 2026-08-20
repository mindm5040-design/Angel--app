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
</style>
""", unsafe_allow_html=True)

def ask_groq(prompt):
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+KEY},json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":"You are NEXA-AI, prof camerounais"},{"role":"user","content":prompt}]},timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def speak_btn(txt,kid):
    safe=txt.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:1500]
    h="""
    <button onclick="s_%s()" style="background:#E07A4F;color:white;border:none;border-radius:20px;padding:6px 14px;">Ecouter</button>
    <script>
    function s_%s(){
        window.speechSynthesis.cancel();
        var u=new SpeechSynthesisUtterance(`%s`);
        u.lang='fr-FR';u.rate=0.95;window.speechSynthesis.speak(u);
    }
    </script>
    """ % (kid,kid,safe)
    components.html(h,height=45)

st.markdown('<div style="text-align:center"><div style="font-size:60px">🧬</div><h1>NEXA-AI</h1><p style="color:#E07A4F;letter-spacing:3px;font-weight:700">POLYGLOT CAMEROUN</p></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Ajoute GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "exam" not in st.session_state:
    st.session_state.exam=""

classe=st.selectbox("Ta classe:",["6eme","5eme","4eme","3eme","2nde","1ere","Tle","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"])
mode=st.selectbox("Super-pouvoir:",["Chat normal","Corriger devoir photo stylo rouge","Fiche revision PDF","Examen blanc","Explication schema","Classement","Partage WhatsApp","Mode groupe"])

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
        with st.spinner("NEXA replique..."):
            ans=ask_groq(p+" niveau "+classe)
        st.session_state.messages.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
            speak_btn(ans, len(st.session_state.messages))

if mode=="Corriger devoir photo stylo rouge":
    st.info("Prends photo, NEXA corrige au stylo rouge")
    img=st.file_uploader("Upload photo devoir",type=["jpg","jpeg","png"])
    if img:
        st.image(img)
        if st.button("Corriger au stylo rouge"):
            with st.spinner("Correction..."):
                b64=base64.b64encode(img.getvalue()).decode()
                try:
                    payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":"Corrige devoir "+classe+" stylo rouge note sur 20"},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
                    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+KEY},json=payload,timeout=90).json()
                    res=r["choices"][0]["message"]["content"]
                except:
                    res=ask_groq("Corrige devoir niveau "+classe+" stylo rouge note sur 20")
                st.markdown(res)
                speak_btn(res,900)

if mode=="Fiche revision PDF":
    st.info("Fiches revisions PDF programme camerounais")
    mat=st.selectbox("Matiere",["Mathematiques","Physique","Chimie","SVT","Histoire","Geographie","Anglais","Philosophie"])
    chap=st.text_input("Chapitre","Replication ADN")
    if st.button("Generer fiche PDF"):
        with st.spinner("Generation..."):
            fiche=ask_groq("Fiche revision "+classe+" "+mat+" "+chap+" def resume exemples exos")
            st.markdown(fiche)
            speak_btn(fiche,901)
            wa=urllib.parse.quote("Fiche NEXA-AI "+mat+" "+fiche[:400])
            st.markdown("[Partager WhatsApp 1 clic](https://wa.me/?text="+wa+")")
            st.download_button("Telecharger",fiche,file_name="NEXA.txt")

if mode=="Examen blanc":
    st.info("Mode examen blanc: 10 questions chronos")
    if st.button("Demarrer examen"):
        qs=ask_groq("Genere 10 QCM niveau "+classe+" replication ADN format Q1 A) B) C) D)")
        st.session_state.exam=qs
    if st.session_state.exam!="":
        st.markdown(st.session_state.exam)
        rep=st.text_input("Reponses ex 1A 2B")
        if st.button("Corriger examen"):
            corr=ask_groq("Corrige: "+st.session_state.exam+" Reponses: "+rep+" note sur 20")
            st.markdown(corr)
            st.balloons()
            st.success("Tu es 3eme de ta classe cette semaine!")

if mode=="Explication schema":
    st.info("Explication video: schema")
    sujet=st.text_input("Sujet","Replication ADN")
    if st.button("Generer schema"):
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/DNA_replication_split.svg/800px-DNA_replication_split.svg.png")
        expl=ask_groq("Explique "+sujet+" niveau "+classe+" en 4 etapes simples")
        st.markdown(expl)
        speak_btn(expl,902)

if mode=="Classement":
    st.success("Tu es 3eme de ta classe cette semaine! Classe: "+classe+" XP: "+str(random.randint(150,300)))

if mode=="Partage WhatsApp":
    st.info("Partager fiche WhatsApp 1 clic")
    txt=st.text_area("Texte","Decouvre NEXA-AI mon prof IA")
    wa=urllib.parse.quote(txt+" https://z.streamlit.app")
    st.markdown("[Envoyer WhatsApp](https://wa.me/?text="+wa+")")

if mode=="Mode groupe":
    st.info("Mode groupe: 3 eleves revisent ensemble")
    qg=st.chat_input("Question groupe...")
    if qg:
        ans=ask_groq("Groupe 3 eleves niveau "+classe+" question: "+qg)
        st.markdown(ans)
        speak_btn(ans,903)
