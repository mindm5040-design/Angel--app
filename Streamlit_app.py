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

/* FORCE LA LIGNE A RESTER HORIZONTALE SUR MOBILE */
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap!important;
    display:flex!important;
    align-items:center!important;
    gap:6px!important;
    max-width:720px; margin:0 auto;
    position:fixed; bottom:10px; left:10px; right:10px;
    background:white; padding:8px; border-radius:30px;
    border:1px solid #e5e5e5; z-index:100;
    box-shadow:0 2px 10px rgba(0,0,0,0.08);
}
div[data-testid="stHorizontalBlock"] div[data-testid="column"] {
    flex-shrink:0!important;
    width:auto!important;
    min-width:0!important;
}
/* La barre de saisie prend tout l'espace au centre */
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) {
    flex-grow:1!important; flex-shrink:1!important; flex-basis:0!important;
}
div[data-testid="stTextInput"] {width:100%!important;}
div[data-testid="stTextInput"] input {
    background:#f0f2f5!important; border:none!important; border-radius:20px!important;
    height:40px!important;
}
.stButton button {border-radius:50%!important; width:38px!important; height:38px!important; padding:0!important; border:1px solid #eee!important; background:white!important;}
.stButton button[kind="primary"] {background:#111!important; color:white!important;}
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

with st.expander("📚 Changer"):
    cols=st.columns(4)
    for i,c in enumerate(CLASSES):
        with cols[i%4]:
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

st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# === MAINTENANT TOUT SUR UNE SEULE LIGNE HORIZONTALE ===
c1,c2,c3,c4,c5 = st.columns([1,1,6,1,1])

with c1:
    if st.button("＋", key="p1"): st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()
with c2:
    if st.button("🖼️", key="p2"): st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()
with c3:
    q = st.text_input("q", placeholder=f"Message en {cl}...", label_visibility="collapsed", key="q_input")
with c4:
    if st.button("🎙️", key="p3"): st.session_state.tool = None if st.session_state.tool=="vocal" else "vocal"; st.rerun()
with c5:
    send = st.button("↑", key="send", type="primary")

if q and q.strip() and q!= st.session_state.get("last_q",""):
    if send or True: # entrée
        st.session_state.last_q = q
        st.session_state.chats[cl].append({"role":"user","content":q})
        st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
        save(); st.rerun()
