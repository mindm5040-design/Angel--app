import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:80px!important; gap:4px!important;}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px 18px 4px 18px!important; padding:10px 14px!important;
}

/* UNE SEULE LIGNE HORIZONTALE */
.bottom-row {max-width:720px; margin:0 auto; position:fixed; bottom:12px; left:12px; right:12px; z-index:100;}
.bottom-row > div {display:flex; align-items:center; gap:8px; background:white; padding:0;}
div[data-testid="stTextInput"] input {
    background:#f4f4f5!important; border:1px solid #e4e4e7!important; border-radius:24px!important;
    padding:12px 16px!important; font-size:15px!important;
}
.stButton button {border-radius:50%!important; width:40px!important; height:40px!important; padding:0!important; border:1px solid #e4e4e7!important; background:white!important;}
.stButton button[kind="primary"] {background:#111!important; color:white!important; border:none!important;}
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
st.markdown(f"<div style='max-width:720px; margin:0 auto;'><b>🕊️ Angel • {cl}</b> <span style='color:#888; font-size:11px;'>• {len(st.session_state.chats[cl])}</span></div>", unsafe_allow_html=True)

with st.expander("📚 Changer", expanded=False):
    cols=st.columns(4)
    for i,c in enumerate(CLASSES):
        with cols[i%4]:
            if st.button(c, key=f"c_{c}", use_container_width=True, type="primary" if c==cl else "secondary"):
                st.session_state.classe=c; st.rerun()

if st.session_state.tool=="photo":
    with st.container(border=True):
        up = st.file_uploader("Photo", type=["jpg","png"], label_visibility="collapsed")
        cam = st.camera_input("Caméra", label_visibility="collapsed")
        img = (cam.getvalue() if cam else None) or (up.getvalue() if up and hasattr(up,'getvalue') else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            ans=ask(f"Résous {cl}", cl, img); st.session_state.chats[cl].extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
            st.session_state.tool=None; save(); st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        aud=st.audio_input("Vocal", label_visibility="collapsed")
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

# === UNE SEULE LIGNE HORIZONTALE : TOUT ALIGNÉ ===
# ＋ | 🖼️ | [ barre de saisie ] | 🎙️ | ↑
c_plus, c_img, c_input, c_mic, c_send = st.columns([0.7, 0.7, 5.2, 0.7, 0.7], gap="small")

with c_plus:
    if st.button("＋", key="plus"):
        st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()

with c_img:
    if st.button("🖼️", key="img"):
        st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()

with c_input:
    q = st.text_input("msg", placeholder=f"Message en {cl}...", label_visibility="collapsed", key="msg_input")

with c_mic:
    if st.button("🎙️", key="mic"):
        st.session_state.tool = None if st.session_state.tool=="vocal" else "vocal"; st.rerun()

with c_send:
    do_send = st.button("↑", key="send", type="primary")

if (do_send or q) and q and q.strip():
    # Si l'utilisateur appuie sur Entrée
    if q!= st.session_state.get("last_q",""):
        st.session_state.last_q = q
        st.session_state.chats[cl].append({"role":"user","content":q})
        st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
        save(); st.rerun()
