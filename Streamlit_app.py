import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

# --- CSS HORIZONTAL FORCE + LONG PRESS ---
st.markdown("""
<style>
.stApp {background:#fff!important;}
header, footer {visibility:hidden!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto;}

/* FORCE BARRE HORIZONTALE */
div[data-testid="stHorizontalBlock"] {
    display:flex!important; flex-direction:row!important; flex-wrap:nowrap!important;
    align-items:center!important; gap:6px!important;
    max-width:720px; margin:0 auto; position:sticky; bottom:0; background:white; padding:8px 0;
    border-top:1px solid #e4e6eb; z-index:99;
}
div[data-testid="column"] {flex:0 0 auto!important; min-width:0!important;}
div[data-testid="column"]:nth-child(5) {flex:1 1 auto!important;}
div[data-testid="column"]:nth-child(1) button, div[data-testid="column"]:nth-child(2) button,
div[data-testid="column"]:nth-child(3) button, div[data-testid="column"]:nth-child(4) button {
    background:#0a27a6!important; color:white!important; border-radius:50%!important; width:40px!important; height:40px!important;
}
div[data-testid="column"]:nth-child(6) button {background:#ff2e2e!important; color:white!important; border-radius:10px!important; width:42px!important; height:42px!important;}
input {background:#f0f2f5!important; border-radius:20px!important;}

/* MESSAGE LONG PRESS */
.msg-box {position:relative; padding:12px; border-radius:12px; margin:6px 0; user-select:none; -webkit-user-select:none;}
.msg-user {background:#e8f0fe; margin-left:auto; max-width:80%; border-radius:18px 18px 4px 18px;}
.msg-assistant {background:#f0f2f5; max-width:80%; border-radius:18px 18px 18px 4px;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")

# RESET SECURISE
if "chats" not in st.session_state or not isinstance(st.session_state.chats, list):
    st.session_state.chats = []
if "tool" not in st.session_state: st.session_state.tool=None
if "classe" not in st.session_state: st.session_state.classe="Master 1"

# SUPPRESSION VIA URL?del=index
if "del" in st.query_params:
    try:
        idx = int(st.query_params["del"])
        if 0 <= idx < len(st.session_state.chats):
            del st.session_state.chats[idx]
            st.query_params.clear()
            st.rerun()
    except: pass

def ask(q, img=None):
    try:
        if img:
            b64=base64.b64encode(img).decode()
            body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
        else:
            body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof {st.session_state.classe}"},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=50).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e: return f"Erreur: {e}"

st.write(f"**🕊️ Angel • {st.session_state.classe}** • {len(st.session_state.chats)} messages")
with st.expander(f"📚 Classe : {st.session_state.classe}"):
    cols=st.columns(4)
    for i,c in enumerate(["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]):
        with cols[i%4]:
            if st.button(c,key=f"cl_{c}"):
                st.session_state.classe=c; st.rerun()

# AFFICHAGE AVEC APPUI LONG 2S
for idx, m in enumerate(st.session_state.chats):
    if not isinstance(m, dict): continue
    role = m.get("role","user")
    content = m.get("content","")
    css_class = "msg-user" if role=="user" else "msg-assistant"
    # HTML avec detection appui long 2s
    st.markdown(f"""
    <div class="msg-box {css_class}" id="msg-{idx}"
         onmousedown="startPress({idx})" onmouseup="cancelPress()" onmouseleave="cancelPress()"
         ontouchstart="startPress({idx})" ontouchend="cancelPress()">
         {content}
         <div style="font-size:10px; color:#888; margin-top:4px;">Appui long 2s pour supprimer</div>
    </div>
    <script>
    let pressTimer;
    function startPress(i){{
        pressTimer = setTimeout(() => {{
            if(confirm('Supprimer ce message?')){{
                window.parent.location.search = '?del=' + i;
            }}
        }}, 2000);
    }}
    function cancelPress(){{ clearTimeout(pressTimer); }}
    </script>
    """, unsafe_allow_html=True)

if st.session_state.tool=="photo":
    up=st.file_uploader("Photo",type=["jpg","png","jpeg"],label_visibility="collapsed")
    cam=st.camera_input("Camera",label_visibility="collapsed")
    img=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser",type="primary"):
        st.session_state.chats = st.session_state.chats + [{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ask("Résous",img)}]
        st.session_state.tool=None; st.rerun()
    if st.button("Fermer"): st.session_state.tool=None; st.rerun()

if st.session_state.tool=="vocal":
    aud=st.audio_input("Parle",label_visibility="collapsed")
    if aud:
        try:
            files={"file":("a.wav",aud.getvalue(),"audio/wav")}
            data={"model":"whisper-large-v3","language":"fr"}
            txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions",headers={"Authorization":f"Bearer {KEY}"},files=files,data=data,timeout=60).json().get("text","")
            if txt:
                st.session_state.chats = st.session_state.chats + [{"role":"user","content":txt},{"role":"assistant","content":ask(txt)}]
                st.session_state.tool=None; st.rerun()
        except: pass
    if st.button("Fermer"): st.session_state.tool=None; st.rerun()

st.divider()
c1,c2,c3,c4,c5,c6 = st.columns([1,1,1,1,4,1], gap="small")
with c1:
    if st.button("➕",key="b1"): st.session_state.tool="photo"; st.rerun()
with c2:
    if st.button("📷",key="b2"): st.session_state.tool="photo"; st.rerun()
with c3:
    if st.button("🖼️",key="b3"): st.session_state.tool="photo"; st.rerun()
with c4:
    if st.button("🎙️",key="b4"): st.session_state.tool="vocal"; st.rerun()
with c5:
    q=st.text_input("q",placeholder="Message",label_visibility="collapsed",key="q_input")
with c6:
    if st.button("➤",key="send",type="primary"):
        if q and q.strip():
            st.session_state.chats = st.session_state.chats + [{"role":"user","content":q},{"role":"assistant","content":ask(q)}]
            st.rerun()
