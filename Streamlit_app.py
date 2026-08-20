import streamlit as st
import requests, os, base64
from pathlib import Path

st.set_page_config(page_title="Angel AI", page_icon="🧬", layout="centered")

# --- CLÉ GROQ ---
def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except: pass
    return os.getenv("GROQ_API_KEY", "")
KEY = get_groq_key()

# --- STYLE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;600&display=swap');
.stApp {background:#FCFCF9!important;}
header, footer, #MainMenu,.stDeployButton {visibility:hidden!important;}
.block-container {padding-top:20px!important;}
.angel-title {font-family:'Space Grotesk';font-size:44px;font-weight:700;text-align:center;margin-top:14px;letter-spacing:-1px;}
@keyframes dnaMove {0%{transform:rotateY(0deg) scale(1)}25%{transform:rotateY(90deg) scale(1.15)}50%{transform:rotateY(180deg) scale(1)}75%{transform:rotateY(270deg) scale(1.15)}100%{transform:rotateY(360deg) scale(1)}}
@keyframes spin {from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes pulse {0%{transform:scale(1)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
@keyframes bounce {0%,80%,100%{transform:translateY(0);opacity:0.5}40%{transform:translateY(-6px);opacity:1}}
</style>
""", unsafe_allow_html=True)

def get_video_html():
    # Si tu as dna.mp4 dans le repo, il l'utilisera, sinon animation CSS
    p = Path("dna.mp4")
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<video style="width:160px;height:160px;border-radius:50%;object-fit:cover;box-shadow:0 0 40px rgba(224,122,79,0.4);border:3px solid #E07A4F;" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    return '''
    <div style="width:160px;height:160px;border-radius:50%;background:white;border:3px solid #E07A4F;box-shadow:0 0 40px rgba(224,122,79,0.35);display:flex;align-items:center;justify-content:center;position:relative;">
      <div style="font-size:72px;animation: dnaMove 2.8s ease-in-out infinite;">🧬</div>
      <div style="position:absolute;inset:-6px;border-radius:50%;border:2px dashed rgba(224,122,79,0.35);animation: spin 5s linear infinite;"></div>
    </div>
    '''

st.markdown(f'''
<div style="display:flex;flex-direction:column;align-items:center;margin:10px 0 30px 0;">
  <div>{get_video_html()}</div>
  <div class="angel-title">Angel AI</div>
  <div style="color:#E07A4F;font-size:11px;letter-spacing:3.5px;font-weight:700;margin-top:6px;font-family:'Space Grotesk';">DNA REPLICATION • ACTIVE</div>
</div>
''', unsafe_allow_html=True)

if not KEY:
    st.warning("⚠️ Ajoute ta clé Groq dans Settings → Secrets → GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe="Master 1"

def ask_groq(q):
    try:
        payload={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, professeur bienveillant niveau {st.session_state.classe}. Réponds clairement avec exemples."},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},json=payload,timeout=60).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur Groq: {e}"

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt=st.chat_input(f"Pose ta question niveau {st.session_state.classe}...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    thinking = st.empty()
    thinking.markdown("""
    <div style="display:flex;align-items:center;gap:12px;background:white;border-radius:20px;padding:14px 18px;border:1px solid #eee;box-shadow:0 2px 10px rgba(0,0,0,0.05);margin-top:10px;">
      <div style="width:38px;height:38px;border-radius:50%;background:#E07A4F;display:flex;align-items:center;justify-content:center;animation: pulse 1.2s infinite;font-size:20px;">🧬</div>
      <div>
        <div style="font-family:'Space Grotesk';font-weight:600;font-size:14px;">Angel réplique son ADN...</div>
        <div style="display:flex;gap:5px;margin-top:5px;">
          <span style="width:6px;height:6px;background:#E07A4F;border-radius:50%;animation: bounce 1.4s infinite;"></span>
          <span style="width:6px;height:6px;background:#E07A4F;border-radius:50%;animation: bounce 1.4s infinite 0.2s;"></span>
          <span style="width:6px;height:6px;background:#E07A4F;border-radius:50%;animation: bounce 1.4s infinite 0.4s;"></span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rep=ask_groq(prompt)
    thinking.empty()
    st.session_state.messages.append({"role":"assistant","content":rep})
    with st.chat_message("assistant"):
        st.markdown(rep)
