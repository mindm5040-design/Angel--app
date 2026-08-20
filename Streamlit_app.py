import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:700px; margin:0 auto; padding-bottom:120px!important; gap:4px!important;}
.stChatMessage p {font-size:15.5px!important; line-height:1.7!important;}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px 18px 4px 18px!important; padding:10px 14px!important;
}

/* PETITS ICONES AUX EXTREMITES */
.small-icon button {
    background:transparent!important; border:none!important;
    font-size:18px!important; color:#65676b!important;
    padding:0!important; height:36px!important; width:36px!important;
    border-radius:50%!important;
}
.small-icon button:hover {background:#f0f2f5!important;}

div[data-testid="stChatInput"] {
    background:#f0f2f5!important; border:none!important; border-radius:20px!important;
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
st.markdown(f"<div style='max-width:700px; margin:0 auto; padding:6px 0;'><b>🕊️ Angel • {cl}</b> <span style='color:#888; font-size:11px;'>• {len(st.session_state.chats[cl])}</span></div>", unsafe_allow_html=True)

# Selecteur classe discret en haut
with st.expander(f"📚 {cl}", expanded=False):
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
        if st.button("Analyser", type="primary", use_container_width=True, disabled=not img):
            ans=ask(f"Résous niveau {cl}", cl, img)
            st.session_state.chats[cl].extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
            st.session_state.tool=None; save(); st.rerun()
        if st.button("✕"): st.session_state.tool=None; st.rerun()

if st.session_state.tool=="vocal":
    with st.container(border=True):
        aud=st.audio_input("", label_visibility="collapsed")
        if aud:
            try:
                files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
                txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
                if txt:
                    st.session_state.chats[cl].append({"role":"user","content":txt})
                    st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)})
                    st.session_state.tool=None; save(); st.rerun()
            except: pass
        if st.button("✕"): st.session_state.tool=None; st.rerun()

for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- BARRE DU BAS AVEC PETITS ICONES AUX EXTREMITES ---
# Extrémité gauche: + Extrémité droite: 📷 🎙️ tout petit
left, center, right1, right2 = st.columns([0.5, 5.5, 0.5, 0.5])

with left:
    st.markdown('<div class="small-icon">', unsafe_allow_html=True)
    if st.button("＋", key="plus"):
        st.session_state.tool = "photo" if st.session_state.tool!="photo" else None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with center:
    q = st.chat_input(f"Message en {cl}...")

with right1:
    st.markdown('<div class="small-icon">', unsafe_allow_html=True)
    if st.button("⊕", key="img"):
        st.session_state.tool = "photo" if st.session_state.tool!="photo" else None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown('<div class="small-icon">', unsafe_allow_html=True)
    if st.button("◉", key="voc"):
        st.session_state.tool = "vocal" if st.session_state.tool!="vocal" else None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if q:
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
