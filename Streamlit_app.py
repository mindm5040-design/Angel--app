import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;600&display=swap');
.stApp {
  background: #fcfcf9!important;
  font-family:'DM Sans', sans-serif!important;
}
/* Grain texture */
.stApp::before {
  content:''; position:fixed; inset:0; pointer-events:none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  z-index:9999;
}
header, footer, #MainMenu {visibility:hidden!important;}

.angel-hero {
  font-family:'Space Grotesk', sans-serif; font-size:42px; font-weight:700;
  letter-spacing:-2px; color:#0a0a0a; line-height:0.9; margin:20px 0 4px;
}
.angel-sub {color:#6b6b6b; font-size:14px; margin-bottom:24px;}

/* BENTO GRID */
.bento {
  display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin:16px 0;
}

/* LIQUID GLASS CARDS */
div[data-testid="stButton"] > button {
  background: rgba(255,255,255,0.7)!important;
  backdrop-filter: blur(20px) saturate(180%)!important;
  -webkit-backdrop-filter: blur(20px) saturate(180%)!important;
  border:1px solid rgba(0,0,0,0.08)!important;
  border-radius:18px!important; height:72px!important;
  font-family:'Space Grotesk', sans-serif!important; font-weight:600!important; font-size:16px!important;
  color:#0a0a0a!important; box-shadow: 0 4px 12px rgba(0,0,0,0.04), inset 0 1px 0 rgba(255,255,255,0.8)!important;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)!important;
  position:relative; overflow:hidden;
}
div[data-testid="stButton"] > button::before {
  content:''; position:absolute; inset:0; border-radius:18px;
  background: radial-gradient(400px circle at var(--mouse-x) var(--mouse-y), rgba(10,39,166,0.08), transparent 40%);
  opacity:0; transition: opacity 0.3s;
}
div[data-testid="stButton"] > button:hover::before {opacity:1;}
div[data-testid="stButton"] > button:hover {
  transform: perspective(600px) rotateX(4deg) rotateY(-4deg) translateY(-4px) scale(1.02)!important;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1), 0 0 0 1px rgba(10,39,166,0.1)!important;
  border-color: rgba(10,39,166,0.15)!important;
}
button[kind="primary"] {
  background: #0a0a0a!important; color:white!important; border:none!important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2)!important;
}

/* BENTO SIZES - Licence et Doctorat plus grands */
div[data-testid="stButton"]:has(button) {grid-column: span 1;}
.bento-large div[data-testid="stButton"] > button {height:88px!important; background: #0a27a6!important; color:white!important;}

/* CHAT - Barely There UI */
div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}
.stChatMessage {background:transparent!important; border:none!important;}
div[data-testid="stChatMessageContent"] {padding:0!important; font-size:15px!important; line-height:1.5!important;}
</style>
<script>
document.addEventListener('mousemove', e => {
  document.querySelectorAll('button').forEach(btn => {
    const rect = btn.getBoundingClientRect();
    btn.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
    btn.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
  });
});
</script>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if not KEY: st.error("Mets GROQ_API_KEY"); st.stop()

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Master 1"

def ask(q, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        payload={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":f"[{st.session_state.classe}] {q}"},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof niveau {st.session_state.classe}"},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=payload,timeout=60).json()
    return r["choices"][0]["message"]["content"]

# HERO - Tendance 2026 Huge Typography
st.markdown("<div class='angel-hero'>Angel.<br>Apprends mieux.</div>", unsafe_allow_html=True)
st.markdown(f"<div class='angel-sub'>Niveau actuel → <b style='color:#0a0a0a'>{st.session_state.classe}</b> • IA locale • Yaoundé</div>", unsafe_allow_html=True)

# BENTO GRID SELECTION
with st.expander(f"Changer de niveau", expanded=True):
    st.markdown("<div style='font-size:11px; letter-spacing:2px; color:#999; font-weight:700; margin-bottom:8px;'>COLLÈGE</div>", unsafe_allow_html=True)
    cols=st.columns(4)
    for i,c in enumerate(["6e","5e","4e","3e"]):
        with cols[i]:
            if st.button(c, key=f"b_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c; st.rerun()
    st.markdown("<div style='font-size:11px; letter-spacing:2px; color:#999; font-weight:700; margin:16px 0 8px;'>LYCÉE</div>", unsafe_allow_html=True)
    cols=st.columns(3)
    for i,c in enumerate(["Seconde","Première","Terminale"]):
        with cols[i]:
            if st.button(c, key=f"b_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c; st.rerun()
    st.markdown("<div style='font-size:11px; letter-spacing:2px; color:#999; font-weight:700; margin:16px 0 8px;'>UNIVERSITÉ — BENTO GRID</div>", unsafe_allow_html=True)
    cols=st.columns(3)
    for i,c in enumerate(["Licence 1","Licence 2","Licence 3"]):
        with cols[i]:
            if st.button(c, key=f"b_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c; st.rerun()
    # Cartes plus grandes pour Master
    cols=st.columns([1.2,1.2,1])
    for i,c in enumerate(["Master 1","Master 2","Doctorat"]):
        with cols[i]:
            if st.button(c, key=f"b_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c; st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

with st.expander("📷 Photo"):
    up=st.file_uploader(" ", type=["jpg","png"], label_visibility="collapsed")
    cam=st.camera_input(" ", label_visibility="collapsed")
    img=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser", type="primary", use_container_width=True):
        rep=ask("Explique", img)
        st.session_state.messages+=[{"role":"user","content":"📷 Photo"},{"role":"assistant","content":rep}]
        st.rerun()

prompt=st.chat_input("Demande à Angel...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    rep=ask(prompt)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.rerun()
