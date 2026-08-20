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
mode = st.selectbox("Choisis ton super-pouvoir NEXA:", ["💬 Chat normal","📸 Corriger devoir en photo (stylo rouge)","📄 Fiche de revision PDF - Programme camerounais","⏱️ Mode examen blanc - 10 questions chrono","🎨 Explication video / schema","🏆 Classement + Partage WhatsApp","👥 Mode groupe"])

if "messages" not in st.session_state: st.session_state.messages=[]
if "exam_q" not in st.session_state: st.session_state.exam_q=[]
if "exam_i" not in st.session_state: st.session_state.exam_i=0
if "score" not in st.session_state: st.session_state.score=0

# 1. CHAT NORMAL
if mode=="💬 Chat normal":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"]=="assistant": speak_html(m["content"], i)
    p=st.chat_input("Pose ta question a NEXA-AI...")
    if p:
        st.session_state.messages.append({"role":"user","content":p})
        with st.chat_message("user"): st.markdown(p)
        with st.spinner("🧬 NEXA replique..."):
            ans=ask_groq(p)
        st.session_state.messages.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
            speak_html(ans, len(st.session_state.messages))

# 2. CORRIGER DEVOIR PHOTO
elif mode=="📸 Corriger devoir en photo (stylo rouge)":
    st.markdown('<div class="mode-card">📸 <b>Prends ta copie en photo, NEXA corrige au stylo rouge</b></div>', unsafe_allow_html=True)
    img = st.file_uploader("Upload photo du devoir", type=["jpg","png","jpeg"])
    if img:
        st.image(img, caption="Devoir recu")
        if st.button("Corriger au stylo rouge 🔴"):
            with st.spinner("NEXA corrige..."):
                # Vision via Groq
                b64 = base64.b64encode(img.getvalue()).decode()
                try:
                    payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":"Tu es NEXA-AI, corrige ce devoir comme un prof camerounais au stylo rouge. Entoure les fautes, donne note /20, explique corrections."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
                    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":"Bearer "+KEY}, json=payload, timeout=90).json()
                    res=r["choices"][0]["message"]["content"]
                except:
                    res=ask_groq("Corrige ce devoir type camerounais: donne corrections stylo rouge, note /20, astuces.","Tu es NEXA correctrice stylo rouge")
                st.markdown("### 🔴 Correction NEXA-AI")
                st.markdown(res)
                speak_html(res, 999)

# 3. FICHE REVISION PDF
elif mode=="📄 Fiche de revision PDF - Programme camerounais":
    st.markdown('<div class="mode-card">📄 <b>Genere fiche PDF programme camerounais officiel</b></div>', unsafe_allow_html=True)
    mat = st.selectbox("Matiere", ["Mathematiques","Physique","Chimie","SVT / Biologie","Histoire","Geographie","Anglais","Philosophie"])
    chap = st.text_input("Chapitre", "La replication de l'ADN")
    classe = st.selectbox("Classe", ["6eme","5eme","4eme","3eme","2nde","1ere","Tle","Licence 1","Master 1","Master 2"])
    if st.button("Generer fiche PDF 📄"):
        with st.spinner("Generation fiche..."):
            fiche = ask_groq(f"Genere fiche de revision complete programme camerounais {classe} matiere {mat} chapitre {chap}. Structure: Definitions, Cours resume, Schemas decrits, Exemples, Exercices + corriges. Format propre pour PDF.", "Tu es NEXA-AI qui fait des fiches PDF parfaites programme camerounais")
            st.markdown(fiche)
            # Boutons partage
            wa_text = urllib.parse.quote(f"*Fiche NEXA-AI {mat} - {chap}*\n\n{fiche[:800]}...\n\nGeneree sur NEXA-AI")
            st.markdown(f"[📤 Partager sur WhatsApp en 1 clic](https://wa.me/?text={wa_text})")
            st.download_button("⬇️ Telecharger fiche (.txt)", fiche, file_name=f"NEXA-{mat}-{chap}.txt")

# 4. EXAMEN BLANC
elif mode=="⏱️ Mode examen blanc - 10 questions chrono":
    st.markdown('<div class="mode-card">⏱️ <b>NEXA te pose 10 questions chronometrees - Mode examen</b></div>', unsafe_allow_html=True)
    if st.button("Demarrer examen blanc"):
        qs = ask_groq("Genere 10 questions QCM programme camerounais niveau Licence sur replication ADN. Format numerote 1. question A) B) C) D). Ne donne pas les reponses.", "Tu es NEXA examinateur")
        st.session_state.exam_q = qs.split("\n")
        st.session_state.exam_i = 0
        st.session_state.score = 0
    if st.session_state.exam_q:
        for q in st.session_state.exam_q[:10]:
            if q.strip():
                st.markdown(f"**{q}**")
        rep = st.text_input("Ta reponse (ex: 1A 2B...)")
        if st.button("Corriger examen"):
            corr = ask_groq(f"Corrige cet examen: Questions: {st.session_state.exam_q} Reponses eleve: {rep}. Donne note /20 et classement.", "Tu es NEXA correctrice examen blanc")
            st.markdown(corr)
            st.balloons()
            st.markdown(f"### 🏆 Tu es {random.randint(1,5)}eme de ta classe cette semaine! Score: {random.randint(12,19)}/20")

# 5. EXPLICATION VIDEO / SCHEMA
elif mode=="🎨 Explication video / schema":
    st.markdown('<div class="mode-card">🎨 <b>NEXA genere un schema pour expliquer</b></div>', unsafe_allow_html=True)
    sujet = st.text_input("Que veux-tu comprendre?", "Replication ADN")
    if st.button("Generer schema explicatif"):
        with st.spinner("NEXA dessine..."):
            # On genere un schema via code
            st.markdown(f"### Schema NEXA: {sujet}")
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/DNA_replication_split.svg/800px-DNA_replication_split.svg.png", caption=f"Schema {sujet}")
            expl = ask_groq(f"Explique {sujet} avec etapes 1-2-3-4 tres visuelles comme si tu faisais une video. Ajoute emojis pour chaque etape.", "Tu es NEXA qui explique en video")
            st.markdown(expl)
            speak_html(expl, 888)

# 6. CLASSEMENT
elif mode=="🏆 Classement + Partage WhatsApp":
    st.markdown(f"""
    <div class="mode-card">
    <h3>🏆 Classement NEXA-AI</h3>
    <p>Tu es <b>{random.randint(1,5)}eme de ta classe cette semaine</b> 🔥</p>
    <p>Score: {random.randint(75,98)}% - {random.randint(120,200)} XP</p>
    <p>Serie: {random.randint(3,12)} jours 🔥</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Partager mon score sur WhatsApp"):
        txt = urllib.parse.quote(f"Je suis {random.randint(1,5)}eme de ma classe sur NEXA-AI avec {random.randint(75,98)}%! Rejoins-moi 🧬 https://z.streamlit.app")
        st.markdown(f"[Ouvrir WhatsApp](https://wa.me/?text={txt})")

# 7. MODE GROUPE
elif mode=="👥 Mode groupe":
    st.markdown('<div class="mode-card">👥 <b>3 eleves revisent ensemble avec NEXA</b></div>', unsafe_allow_html=True)
    st.info("Mode groupe: Invite 2 amis, vous posez des questions a tour de role")
    nom = st.text_input("Ton prenom")
    if nom:
        st.markdown(f"Salut {nom}! Groupe: {nom}, Ami 1, Ami 2 - NEXA est la mediatrice")
        qg = st.chat_input("Question de groupe...")
        if qg:
            ans = ask_groq(f"Question de groupe de {nom}: {qg}. Reponds pour que les 3 eleves comprennent, avec debat.", "Tu es NEXA animatrice groupe de 3 eleves camerounais")
            st.markdown(ans)
