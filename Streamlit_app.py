import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:100px!important; gap:4px!important;}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px 18px 4px 18px!important; padding:10px 14px!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stMarkdownContainer"]{
    background:transparent!important;
}

/* BARRE PRO COMME CLAUDE / CHATGPT */
.pro-bar {
    max-width:720px; margin:0 auto;
    background:#f4f4f5; border:1px solid #e4e4e7; border-radius:26px;
    display:flex; align-items:center; padding:6px 8px; gap:6px;
    position:fixed; bottom:18px; left:12px; right:12px; z-index:100;
    box-shadow:0 4px 20px rgba(0,0,0,0.06);
}
.pro-bar input {
    flex:1; border:none!important; background:transparent!important;
    outline:none!important; font-size:15px; padding:8px 4px;
}
.icon-btn {
    width:32px; height:32px; border-radius:50%; border:none;
    background:transparent; color:#71717a; cursor:pointer; font-size:18px;
    display:flex; align-items:center; justify-content:center;
}
.icon-btn:hover {background:#e4e4e7;}
.send-btn {background:#111!important; color:white!important;}
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

# HEADER
st.markdown(f"<div style='max-width:720px; margin:0 auto; padding:8px 0;'><b>🕊️ Angel • {cl}</b> <span style='color:#888; font-size:11px;'>• {len(st.session_state.chats[cl])}</span></div>", unsafe_allow_html=True)
with st.expander(f"Changer classe", expanded=False):
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
        if st.button("Analyser", type="primary", use_container_width=True, disabled=not img):
            ans=ask(f"Résous {cl}", cl, img); st.session_state.chats[cl].extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
            st.session_state.tool=None; save(); st.rerun()
        if st.button("Fermer", use_container_width=True): st.session_state.tool=None; st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        aud=st.audio_input("Vocal", label_visibility="collapsed")
        if aud:
            try:
                files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
                txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
                if txt:
                    st.session_state.chats[cl].append({"role":"user","content":txt})
                    st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)})
                    st.session_state.tool=None; save(); st.rerun()
            except: pass

for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- VRAIE BARRE PRO COMME CLAUDE ---
# Une seule barre, icônes dedans
c1,c2,c3,c4,c5 = st.columns([0.6, 0.6, 6, 0.6, 0.6])

with c1:
    if st.button("＋", key="plus_pro", help="Fichiers"):
        st.session_state.tool = "photo" if st.session_state.tool!="photo" else None; st.rerun()

with c2:
    # petit icône image à côté du +
    if st.button("🖼️", key="img_pro"):
        st.session_state.tool = "photo" if st.session_state.tool!="photo" else None; st.rerun()

with c3:
    q = st.chat_input(f"Écrire à Angel...")

with c4:
    if st.button("🎙️", key="mic_pro"):
        st.session_state.tool = "vocal" if st.session_state.tool!="vocal" else None; st.rerun()

with c5:
    if st.button("↑", key="send_pro", type="primary"):
        st.toast("Écris ton message dans la barre du centre")

if q:
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
