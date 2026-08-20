import streamlit as st
import requests
import base64
from pathlib import Path

# ================= CONFIG =================
st.set_page_config(
    page_title="Angel AI - Apprends mieux",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= STYLES HIGH-TECH 2026 =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Sans:wght@400;500;600&display=swap');

.stApp {
  background: #FCFCF9!important;
  font-family: 'DM Sans', sans-serif!important;
}
/* Grain subtil 2026 */
.stApp::before {
  content:''; position:fixed; inset:0; pointer-events:none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  z-index:9999;
}
header, footer, #MainMenu,.stDeployButton {visibility:hidden!important;}

/* HERO */
.brain-container {display:flex; flex-direction:column; align-items:center; justify-content:center; margin:12px 0 8px;}
.brain-video {
  width:148px; height:148px; border-radius:50%; object-fit:cover;
  box-shadow: 0 0 0 1px rgba(224,122,79,0.2), 0 0 40px rgba(224,122,79,0.25), 0 12px 32px rgba(0,0,0,0.12);
  border: 1.5px solid #E07A4F;
  animation: floatBrain 4s ease-in-out infinite;
}
@keyframes floatBrain {0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)}}
.angel-title {
  font-family:'Space Grotesk', sans-serif; font-size:46px; font-weight:700;
  letter-spacing:-2.5px; color:#0a0a0a; line-height:0.9; text-align:center; margin-top:18px;
}
.angel-badge {
  display:inline-flex; align-items:center; gap:6px;
  background:#0a0a0a; color:white; font-size:10px; letter-spacing:2px; font-weight:700;
  padding:6px 12px; border-radius:100px; margin-top:10px;
}
.angel-badge.dot {width:6px; height:6px; background:#22c55e; border-radius:50%; box-shadow:0 0 8px #22c55e; animation:pulseDot 1.5s infinite;}
@keyframes pulseDot {0%,100%{opacity:1} 50%{opacity:0.5}}

/* BENTO BUTTONS - Liquid Glass 2.0 */
div[data-testid="stButton"] > button {
  background: rgba(255,255,255,0.72)!important;
  backdrop-filter: blur(20px) saturate(180%)!important;
  -webkit-backdrop-filter: blur(20px) saturate(180%)!important;
  border: 1px solid rgba(0,0,0,0.06)!important;
  border-radius: 18px!important;
  height: 74px!important;
  font-family:'Space Grotesk', sans-serif!important;
  font-weight:600!important; font-size:15px!important;
  color:#0a0a0a!important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04), inset 0 1px 0 rgba(255,255,255,0.9)!important;
  transition: all 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275)!important;
}
div[data-testid="stButton"] > button:hover {
  transform: perspective(600px) rotateX(3deg) rotateY(-3deg) translateY(-4px) scale(1.02)!important;
  box-shadow: 0 20px 40px rgba(0,0,0,0.10), 0 0 0 1px rgba(224,122,79,0.15)!important;
  border-color: rgba(224,122,79,0.25)!important;
}
button[kind="primary"] {
  background: #0a0a0a!important; color:white!important; border:none!important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18)!important;
}
button[kind="primary"]:hover {background:#E07A4F!important;}

/* CHAT */
div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}
.stChatMessage {background:transparent!important; border:none!important;}
div[data-testid="stChatMessageContent"] {font-size:15.5px!important; line-height:1.6!important;}
.stChatInput {border-radius:16px!important;}
</style>
""", unsafe_allow_html=True)

# ================= LOGO VIDEO =================
def get_video_html():
    p = Path("brain.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video class="brain-video" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    else:
        # Fallback si pas de vidéo
        return '<div style="width:148px; height:148px; border-radius:50%; background:#0a0a0a; display:flex; align-items:center; justify-content:center; font-size:64px;">🧠</div>'

st.markdown(f"""
<div class="brain-container">
  {get_video_html()}
  <div class="angel-title">Angel</div>
  <div class="angel-badge"><span class="dot"></span> NEURAL ENGINE • ACTIVE</div>
</div>
""", unsafe_allow_html=True)

# ================= LOGIC =================
KEY = st.secrets.get("GROQ_API_KEY", "")
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans.streamlit/secrets.toml")
    st.code('GROQ_API_KEY="gsk_..."')
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "classe" not in st.session_state:
    st.session_state.classe = "Master 1"

def ask_groq(question, image_bytes=None):
    if image_bytes:
        img_b64 = base64.b64encode(image_bytes).decode()
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"[Niveau {st.session_state.classe}] {question}. Explique clairement étape par étape."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }],
            "temperature": 0.3
        }
    else:
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": f"Tu es Angel AI, le meilleur professeur particulier. Niveau de l'élève: {st.session_state.classe}. Tu expliques simplement, avec exemples, sans jargon inutile. Tu es bienveillant et direct."},
                {"role": "user", "content": question}
            ],
            "temperature": 0.4
        }
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=70
        ).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

# ================= SELECTEUR NIVEAU - BENTO GRID =================
with st.expander(f"📚 Niveau actuel : {st.session_state.classe} — Changer", expanded=False):
    st.markdown('<div style="font-size:10px; letter-spacing:2.5px; color:#999; font-weight:700; margin:8px 0 8px;">COLLÈGE</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, name in zip([c1,c2,c3,c4], ["6e","5e","4e","3e"]):
        with col:
            if st.button(name, key=f"cl_{name}", use_container_width=True, type="primary" if st.session_state.classe==name else "secondary"):
                st.session_state.classe = name; st.rerun()

    st.markdown('<div style="font-size:10px; letter-spacing:2.5px; color:#999; font-weight:700; margin:16px 0 8px;">LYCÉE</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, name in zip([c1,c2,c3], ["Seconde","Première","Terminale"]):
        with col:
            if st.button(name, key=f"cl_{name}", use_container_width=True, type="primary" if st.session_state.classe==name else "secondary"):
                st.session_state.classe = name; st.rerun()

    st.markdown('<div style="font-size:10px; letter-spacing:2.5px; color:#999; font-weight:700; margin:16px 0 8px;">UNIVERSITÉ</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, name in zip([c1,c2,c3], ["Licence 1","Licence 2","Licence 3"]):
        with col:
            if st.button(name, key=f"cl_{name}", use_container_width=True, type="primary" if st.session_state.classe==name else "secondary"):
                st.session_state.classe = name; st.rerun()

    c1, c2, c3 = st.columns([1.3,1.3,1])
    for col, name in zip([c1,c2,c3], ["Master 1","Master 2","Doctorat"]):
