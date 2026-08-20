import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:110px!important; gap:4px!important;}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px 18px 4px 18px!important; padding:10px 14px!important;
}

/* BARRE COMME TA CAPTURE */
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap!important; flex-direction:row!important;
    display:flex!important; align-items:center!important;
    gap:10px!important; max-width:720px; margin:0 auto;
    position:fixed; bottom:0; left:0; right:0;
    background:white!important; padding:10px 12px!important;
    border-top:1px solid #e4e6eb!important; z-index:999;
}
/* Icones bleues rondes comme ta capture */
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) button,
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) button,
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) button,
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(4) button {
    background:#0a24a8!important; border:none!important;
    border-radius:50%!important; width:36px!important; height:36px!important;
    color:white!important; font-size:18px!important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(5) input {
    background:#f0f2f5!important; border:none!important; border-radius:20px!important; height:38px!important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(6) button {
    background:#0a24a8!important; border-radius:50%!important; width:36px!important; height:36px!important; color:white!important;
}
</style>
""", unsafe_allow_html=True)

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
FILE = "angel_memory.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {c: [] for c in CLASSES}
def save():
    with open(FILE,"w",encoding="utf-8") as f: json.dump(st.session_state.chats, f, ensure_ascii=False, indent=2)

if "chats" not in st.session_state: st.session_state.chats = load()
if "classe" not in st.session_state: st.session_state.classe = "Terminale"
if "tool" not in st.session_state: st.session_state.tool = None

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def ask(q, classe, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}"},{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}."},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=40).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur"

cl = st.session_state.classe
st.markdown(f"<div style='max-width:720px; margin:0 auto; padding:6px 0;'><b>🕊️ Angel • {cl}</b> <span style='color:#888; font-size:11px;'>• {len(st.session_state.chats[cl])}</span></div>", unsafe_allow_html=True)

with st.expander(f"📚 {cl}", expanded=False):
    cs=st.columns(4)
    for i,c in enumerate(CLASSES):
        with cs[i%4]:
            if st.button(c, key=f"c_{c}", use_container_width=True, type="primary" if c==cl else "secondary"):
                st.session_state.classe=c; st.rerun()

if st.session_state.tool=="photo":
    with st.container(border=True):
        up = st.file_uploader("", type=["jpg","png"], label_visibility="collapsed")
        cam = st.camera_input("", label_visibility="collapsed")
        img = (cam.getvalue() if cam else None) or (up.getvalue() if up and hasattr(up,'getvalue') else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            ans=ask(f"Résous {cl}", cl, img); st.session_state.chats[cl].extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
            st.session_state.tool=None; save(); st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        aud=st.audio_input("", label_visibility="collapsed")
        if aud:
            try:
                files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
                txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
                if txt:
                    st.session_state.chats[cl].extend([{"role":"user","content":txt},{"role":"assistant","content":ask(txt, cl)}])
                    st.session_state.tool=None; save(); st.rerun()
            except: pass

for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

st.markdown("<div style='height:90px;'></div>", unsafe_allow_html=True)

# ===== EXACTEMENT COMME TA CAPTURE =====
# [ + ] [ 📷 ] [ 🖼️ ] [ 🎙️ ] [ Message ] [ ➤ ]
b1,b2,b3,b4,b5,b6 = st.columns([0.7,0.7,0.7,0.7,4.5,0.7], gap="small")

with b1:
    if st.button("＋", key="plus_final"): st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()
with b2:
    if st.button("◎", key="cam_final"): st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()
with b3:
    if st.button("◫", key="gal_final"): st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()
with b4:
    if st.button("🎙️", key="mic_final"): st.session_state.tool = None if st.session_state.tool=="vocal" else "vocal"; st.rerun()
with b5:
    q = st.text_input("msg", placeholder="Message", label_visibility="collapsed", key="msg_final")
with b6:
    send = st.button("➤", key="send_final")

if q and q.strip() and q!= st.session_state.get("last_q",""):
    st.session_state.last_q = q
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
