import streamlit as st
import requests, os, base64
import streamlit.components.v1 as components

st.set_page_config(page_title="NEX-AI - Par Lelouch", page_icon="⚡️", layout="centered")

KEY = st.secrets.get("GROQ_API_KEY", "") if "GROQ_API_KEY" in st.secrets else os.getenv("GROQ_API_KEY","")

st.markdown("""
<style>
.stApp{background:#0A0A0B!important;color:white!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.stChatMessage{background:#1A1A1D!important;border-radius:16px!important;}
h1,h2,h3,p,span,label{color:white!important;}
.nex-title{font-size:40px;font-weight:900;text-align:center;letter-spacing:-1px;}
.nex-sub{color:#7C3AED!important;font-size:11px;letter-spacing:3px;font-weight:800;text-align:center;}
</style>
""", unsafe_allow_html=True)

# --- HEADER NEX-AI ---
st.markdown("""
<div style="text-align:center;margin:25px 0;">
<div style="font-size:65px;">⚡️</div>
<div class="nex-title">NEX-AI</div>
<div class="nex-sub">NEURAL EXCELLENCE - ACTIVE</div>
<div style="margin-top:10px;font-size:12px;background:#1A1A1D;border:1px solid #7C3AED;border-radius:20px;display:inline-block;padding:5px 14px;">Créateur: Lelouch ✅ | Yaoundé | NEX-01</div>
</div>
""", unsafe_allow_html=True)

niveau = st.selectbox("🎓 Niveau :", ["6e","5e","4e","3e","2nde","1ère","Terminale","Université","Doctorat"], index=6)

if not KEY:
    st.warning("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def speak_button(text, id):
    safe = text.replace("'"," ").replace('"'," ").replace("\n"," ")[:2000]
    components.html(f"""
    <button onclick="speak_{id}()" style="background:#7C3AED;color:white;border:none;border-radius:20px;padding:6px 14px;cursor:pointer;">🔊 Écouter NEX</button>
    <script>function speak_{id}(){{speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(`{safe}`);u.lang='fr-FR';u.rate=0.97;speechSynthesis.speak(u);}}</script>
    """, height=40)

def ask_groq(prompt, image_b64=None):
    msgs = [{"role":"system","content":f"Tu es NEX-AI, une IA créée par Lelouch à Yaoundé. Tu es surpuissante, rapide, bienveillante. Tu expliques au niveau {niveau}. Tu t'appelles NEX-AI, pas Angel. Réponds en français."}]
    if image_b64:
        msgs.append({"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{image_b64}"}}]})
        model="llama-3.2-90b-vision-preview"
    else:
        msgs.append({"role":"user","content":prompt})
        model="llama-3.1-70b-versatile"
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json={"model":model,"messages":msgs},timeout=90)
    return r.json()["choices"][0]["message"]["content"]

col1, col2 = st.columns(2)
with col1:
    photo = st.file_uploader("📸 Photo exo", type=["jpg","png","jpeg"])
with col2:
    audio = st.audio_input("🎤 Vocal")

for i,m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"]=="assistant":
            speak_button(m["content"], i)

user_text=None
img_b64=None
if photo:
    img_b64=base64.b64encode(photo.read()).decode()
    user_text=f"Analyse cette photo d'exercice niveau {niveau}"
if audio:
    user_text=f"Question vocale niveau {niveau}, réponds."

prompt = st.chat_input(f"Question à NEX-AI niveau {niveau}...")
if prompt: user_text=prompt

if user_text:
    st.session_state.messages.append({"role":"user","content":user_text if not photo else "📸 "+user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
        if photo: st.image(photo, width=200)
    with st.chat_message("assistant"):
        with st.spinner(f"NEX-AI calcule niveau {niveau}... ⚡️"):
            ans=ask_groq(user_text, img_b64)
        st.markdown(ans)
        speak_button(ans, len(st.session_state.messages))
    st.session_state.messages.append({"role":"assistant","content":ans})
