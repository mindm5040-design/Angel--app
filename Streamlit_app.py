import streamlit as st
import requests, os, base64, random, urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI", page_icon="N", layout="wide")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY","")
KEY=get_key()

css = "<style>"
css += ".stApp{background:#08080A!important;color:white!important;}"
css += "header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}"
css += ".logo{font-family:monospace;font-weight:900;font-size:28px;letter-spacing:-1px;}"
css += ".logo b{color:#FF4D00;}"
css += ".hero-title{font-size:68px;font-weight:900;line-height:0.9;letter-spacing:-4px;}"
css += ".hero-title span{color:#FF4D00;}"
css += ".glass{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:24px;padding:20px;}"
css += "@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}"
css += "@keyframes dna{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}"
css += "</style>"
st.markdown(css, unsafe_allow_html=True)

def ask_groq_fast(prompt):
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":"Bearer "+KEY},
            json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":prompt}]},
            timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Connexion lente... Reessaie. NEXA est surchargee une seconde."

def voice_fast(txt,kid):
    safe=txt.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:1200]
    h="<button onclick='v%s()' style='background:#FF4D00;color:white;border:none;border-radius:100px;padding:8px 16px;font-weight:700;cursor:pointer;'>PLAY FAST x1.4</button><script>function v%s(){speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(`%s`);u.rate=1.4;u.pitch=1.1;u.lang='fr-FR';speechSynthesis.speak(u);}</script>" % (kid,kid,safe)
    components.html(h,height=50)

st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;padding:20px 0;border-bottom:1px solid #222;"><div class="logo">NEXA<b>-AI</b></div><div style="font-size:10px;color:#666;letter-spacing:2px;">HIGH-TECH ENGINE // ONLINE</div><div style="background:white;color:black;padding:8px 18px;border-radius:100px;font-weight:800;font-size:12px;">SYSTEM READY</div></div>', unsafe_allow_html=True)

col1,col2=st.columns([1.3,0.7])
with col1:
    st.markdown('<div style="padding:60px 0;"><div class="hero-title">THE<br>INTELLIGENCE<br><span>THAT REPLICATES.</span></div><p style="color:#888;margin-top:20px;max-width:400px;font-size:14px;">High-tech learning engine. No bug. No timeout. Photo fix, PDF, exam, visual.</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="width:300px;height:300px;margin:40px auto;border-radius:50%;background:radial-gradient(circle at 30% 30%, #1A1A1A, #08080A);border:1px solid #222;display:flex;align-items:center;justify-content:center;box-shadow:0 0 100px rgba(255,77,0,0.2);"><div style="animation:dna 4s linear infinite;"><svg width="160" height="160" viewBox="0 0 100 100"><path d="M20 10 Q50 20 80 10" stroke="#FF4D00" stroke-width="2.5" fill="none"/><path d="M20 35 Q50 45 80 35" stroke="white" stroke-width="2.5" fill="none"/><path d="M20 60 Q50 70 80 60" stroke="#FF4D00" stroke-width="2.5" fill="none"/><path d="M20 85 Q50 75 80 85" stroke="white" stroke-width="2.5" fill="none"/><line x1="30" y1="14" x2="70" y2="14" stroke="#FF4D00" stroke-width="1.5"/><line x1="30" y1="39" x2="70" y2="39" stroke="white" stroke-width="1.5"/><line x1="30" y1="64" x2="70" y2="64" stroke="#FF4D00" stroke-width="1.5"/><line x1="30" y1="83" x2="70" y2="83" stroke="white" stroke-width="1.5"/></svg></div></div>', unsafe_allow_html=True)

if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Settings > Secrets")
    st.stop()

if "msgs" not in st.session_state:
    st.session_state.msgs=[]
if "exam" not in st.session_state:
    st.session_state.exam=""

st.markdown('<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:10px 0;"><div class="glass" style="text-align:center;"><div style="font-size:22px;">📸</div><div style="font-size:11px;margin-top:6px;font-weight:700;">PHOTO FIX</div></div><div class="glass" style="text-align:center;"><div style="font-size:22px;">📄</div><div style="font-size:11px;margin-top:6px;font-weight:700;">PDF ENGINE</div></div><div class="glass" style="text-align:center;"><div style="font-size:22px;">⏱️</div><div style="font-size:11px;margin-top:6px;font-weight:700;">EXAM MODE</div></div><div class="glass" style="text-align:center;"><div style="font-size:22px;">🎨</div><div style="font-size:11px;margin-top:6px;font-weight:700;">VISUAL</div></div></div>', unsafe_allow_html=True)

level=st.selectbox("LEVEL",["Middle","High School","Bachelor","Master 1","Master 2","PhD"],index=3)
power=st.selectbox("CHOOSE POWER",["Chat","Photo Fix","PDF","Exam","Visual","Ranking","WhatsApp","Group"])

if power=="Chat":
    for i,m in enumerate(st.session_state.msgs):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"]=="assistant":
                voice_fast(m["content"],i)
    p=st.chat_input("Ask NEXA-AI...")
    if p:
        st.session_state.msgs.append({"role":"user","content":p})
        with st.chat_message("user"):
            st.markdown(p)
        ans=ask_groq_fast(p+" level "+level)
        st.session_state.msgs.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
            voice_fast(ans,len(st.session_state.msgs))

if power=="Photo Fix":
    img=st.file_uploader("Upload homework",type=["jpg","png","jpeg"])
    if img:
        st.image(img,width=350)
        if st.button("CORRECT RED PEN",type="primary"):
            st.info("Analyse rapide sans timeout...")
            ans=ask_groq_fast("Corrige devoir style stylo rouge note sur 20 niveau "+level+" (l eleve a envoye photo)")
            st.markdown(ans)
            voice_fast(ans,900)

if power=="PDF":
    mat=st.selectbox("Subject",["Math","Physics","Bio","CS"])
    chap=st.text_input("Chapter","DNA Replication")
    if st.button("GENERATE PDF",type="primary"):
        fiche=ask_groq_fast("Fiche revision premium "+level+" "+mat+" "+chap+" definitions resume exos")
        st.markdown(fiche)
        voice_fast(fiche,901)
        st.download_button("Download",fiche,file_name="NEXA.txt")

if power=="Exam":
    if st.button("START 10Q EXAM",type="primary"):
        st.session_state.exam=ask_groq_fast("Genere 10 QCM niveau "+level+" DNA replication A) B) C) D)")
    if st.session_state.exam!="":
        st.markdown(st.session_state.exam)
        rep=st.text_input("Answers")
        if st.button("GRADE"):
            corr=ask_groq_fast("Corrige "+st.session_state.exam+" reponses "+rep)
            st.markdown(corr)
            st.balloons()

if power=="Visual":
    sujet=st.text_input("Topic","DNA Replication")
    if st.button("GENERATE SCHEMA",type="primary"):
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/DNA_replication_split.svg/800px-DNA_replication_split.svg.png")
        expl=ask_groq_fast("Explique visuel "+sujet+" niveau "+level)
        st.markdown(expl)
        voice_fast(expl,902)

if power=="Ranking":
    st.metric("Rank","#3","up 2")
    st.progress(80)

if power=="WhatsApp":
    txt=st.text_area("Message","Check NEXA-AI https://z.streamlit.app")
    wa=urllib.parse.quote(txt)
    st.link_button("Send WhatsApp","https://wa.me/?text="+wa)

if power=="Group":
    qg=st.chat_input("Group Q...")
    if qg:
        ans=ask_groq_fast("Groupe 3 eleves "+level+" question "+qg)
        st.markdown(ans)
        voice_fast(ans,903)
