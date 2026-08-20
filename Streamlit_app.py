import streamlit as st
import requests, base64, json, os

st.set_page_config(page_title="Angel - Ton assistant", page_icon="🕊️", layout="centered")

# --- DESIGN IMPECCABLE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap');
.stApp {background:#ffffff!important; font-family:'Inter',sans-serif!important;}
header, footer, [data-testid="stHeader"] {visibility:hidden!important; height:0!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:20px!important; gap:12px!important;}

/* BULLES CHAT */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    flex-direction:row-reverse!important; max-width:78%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#e8f0fe!important; border-radius:20px 20px 4px 20px!important; padding:10px 16px!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stMarkdownContainer"]{
    background:#f0f2f5!important; border-radius:20px 20px 20px 4px!important; padding:10px 16px!important;
}

/* --- BARRE DU BAS EXACTEMENT COMME TON IMAGE --- */
div[data-testid="stHorizontalBlock"].bottom-bar {
    display:flex!important; flex-direction:row!important; flex-wrap:nowrap!important;
    align-items:center!important; gap:8px!important;
    max-width:720px; margin:10px auto 0 auto!important;
    background:white!important; padding:10px 8px!important;
    border-top:1px solid #e4e6eb!important;
    position:sticky!important; bottom:0!important; z-index:99!important;
}
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]{
    flex:0 0 auto!important; min-width:auto!important; width:auto!important; padding:0!important;
}
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]:nth-child(5){
    flex:1 1 auto!important;
}

/* LES 4 RONDS BLEUS */
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]:nth-child(1) button,
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]:nth-child(2) button,
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]:nth-child(3) button,
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]:nth-child(4) button{
    background:#0a27a6!important; color:white!important; border:none!important;
    width:40px!important; height:40px!important; border-radius:50%!important;
    font-size:18px!important; box-shadow:none!important;
}

/* BULLE MESSAGE GRISE */
div[data-testid="stHorizontalBlock"].bottom-bar input{
    background:#f0f2f5!important; border:none!important; border-radius:22px!important;
    height:42px!important; padding-left:18px!important; font-size:15px!important;
}

/* BOUTON ENVOI ROUGE A DROITE */
div[data-testid="stHorizontalBlock"].bottom-bar div[data-testid="column"]:nth-child(6) button{
    background:#ff2e2e!important; color:white!important; border-radius:12px!important;
    width:42px!important; height:42px!important; font-size:18px!important;
}
</style>
""", unsafe_allow_html=True)

FILE = "angel_memory.json"
CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
KEY = st.secrets.get("GROQ_API_KEY","").strip()

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f:
                d=json.load(f)
                if isinstance(d, dict): return {c:[] for c in CLASSES}
                return d if isinstance(d, list) else []
        except: pass
    return []

def save(data):
    try:
        with open(FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
    except: pass

if "chats" not in st.session_state: st.session_state.chats=load()
if "tool" not in st.session_state: st.session_state.tool=None
if "classe" not in st.session_state: st.session_state.classe="Terminale"
if "last_q" not in st.session_state: st.session_state.last_q=""

def ask(q, img=None):
    try:
        if img:
            b64=base64.b64encode(img).decode()
            body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":f"[{st.session_state.classe}] {q}"},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
        else:
            body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof de {st.session_state.classe}, tu expliques simple et clair."},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization": f"Bearer {KEY}"},json=body,timeout=40).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e: return f"Erreur: {e}"

# --- HEADER ---
st.markdown(f"<div style='max-width:720px; margin:0 auto 10px auto; display:flex; justify-content:space-between; align-items:center;'><div><b style='font-size:18px;'>🕊️ Angel</b> <span style='color:#65676b; font-size:13px;'>• {st.session_state.classe}</span></div><div style='color:#65676b; font-size:12px;'>{len(st.session_state.chats)} messages</div></div>", unsafe_allow_html=True)

# --- SELECTEUR CLASSE ---
with st.expander(f"📚 Classe : {st.session_state.classe}", expanded=False):
    cols=st.columns(4)
    for i,c in enumerate(CLASSES):
        with cols[i%4]:
            if st.button(c,key=f"cl_{c}",use_container_width=True,type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe=c; st.rerun()

# --- CHAT ---
for m in st.session_state.chats:
    if not isinstance(m, dict) or "role" not in m: continue
    role = m.get("role","user")
    if role not in ["user","assistant"]: continue
    with st.chat_message(role):
        st.markdown(m.get("content",""))

# --- OUTILS ---
if st.session_state.tool=="photo":
    with st.container(border=True):
        st.markdown("**📷 Envoie ta photo**")
        up=st.file_uploader("",type=["jpg","jpeg","png"],label_visibility="collapsed")
        cam=st.camera_input("",label_visibility="collapsed")
        img=cam.getvalue() if cam else (up.getvalue() if up and hasattr(up,'getvalue') else None)
        cA,cB=st.columns(2)
        with cA:
            if img and st.button("Analyser",type="primary",use_container_width=True):
                ans=ask("Résous cet exercice explique étape par étape",img)
                st.session_state.chats.extend([{"role":"user","content":"📷 Photo d'exercice"},{"role":"assistant","content":ans}])
                save(st.session_state.chats); st.session_state.tool=None; st.rerun()
        with cB:
            if st.button("Fermer",use_container_width=True): st.session_state.tool=None; st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        st.markdown("**🎙️ Parle**")
        aud=st.audio_input("",label_visibility="collapsed")
        if aud:
            try:
                files={"file":("a.wav",aud.getvalue(),"audio/wav")}
                data={"model":"whisper-large-v3","language":"fr"}
                txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions",headers={"Authorization": f"Bearer {KEY}"},files=files,data=data,timeout=60).json().get("text","")
                if txt:
                    st.session_state.chats.extend([{"role":"user","content":txt},{"role":"assistant","content":ask(txt)}])
                    save(st.session_state.chats); st.session_state.tool=None; st.rerun()
            except: pass

# --- BARRE EXACTE DE TON IMAGE ---
st.markdown('<div class="bottom-bar-anchor"></div>', unsafe_allow_html=True)
# On injecte une classe pour cibler seulement
