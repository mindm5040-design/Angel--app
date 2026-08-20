import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:110px!important; gap:4px!important;}
.stChatMessage p {font-size:15.5px!important; line-height:1.7!important;}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px 18px 4px 18px!important; padding:10px 14px!important;
}

/* BARRE DU BAS ELEGANTE */
.bottom-bar {
    position:fixed; bottom:0; left:0; right:0;
    background:white; border-top:1px solid #e5e5e5;
    padding:8px 12px; display:flex; align-items:center; gap:8px;
    max-width:720px; margin:0 auto; z-index:100;
}
div[data-testid="stChatInput"] {
    max-width:720px; margin:0 auto; background:#f0f2f5!important;
    border-radius:20px!important; border:none!important; flex:1;
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

# HEADER
h1,h2 = st.columns([3,1])
with h1: st.markdown(f"**🕊️ Angel • {cl}** <span style='color:#888; font-size:12px;'>• {len(st.session_state.chats[cl])}</span>", unsafe_allow_html=True)
with h2:
    new_cl = st.selectbox("classe", CLASSES, index=CLASSES.index(cl), label_visibility="collapsed")
    if new_cl!=cl: st.session_state.classe=new_cl; st.rerun()

# TOOL PANELS (s'ouvrent au dessus de la barre)
if st.session_state.tool == "photo":
    with st.container(border=True):
        up = st.file_uploader("Photo", type=["jpg","png"], label_visibility="collapsed")
        cam = st.camera_input("Caméra", label_visibility="collapsed")
        c1,c2 = st.columns(2)
        if c1.button("Fermer", use_container_width=True): st.session_state.tool=None; st.rerun()
        img_data = (cam.getvalue() if cam else None) or (up.getvalue() if up and hasattr(up,'getvalue') else None)
        if c2.button("Analyser", use_container_width=True, type="primary", disabled=not img_data):
            ans = ask(f"Résous niveau {cl}", cl, img_data)
            st.session_state.chats[cl].extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
            st.session_state.tool=None; save(); st.rerun()

if st.session_state.tool == "vocal":
    with st.container(border=True):
        aud = st.audio_input("Vocal", label_visibility="collapsed")
        if st.button("Fermer", use_container_width=True): st.session_state.tool=None; st.rerun()
        if aud:
            try:
                files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
                txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
                if txt:
                    st.session_state.chats[cl].append({"role":"user","content":txt})
                    st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)})
                    st.session_state.tool=None; save(); st.rerun()
            except: pass

# CHAT
for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- BARRE DU BAS AVEC ICONES A COTE ---
# On crée la rangée élégante
b1,b2,b3,b4 = st.columns([0.8,0.8,6,0.8])
with b1:
    if st.button("📷", use_container_width=True):
        st.session_state.tool = None if st.session_state.tool=="photo" else "photo"; st.rerun()
with b2:
    if st.button("🎙️", use_container_width=True):
        st.session_state.tool = None if st.session_state.tool=="vocal" else "vocal"; st.rerun()
with b3:
    q = st.text_input("Message", placeholder=f"Écris à Angel en {cl}...", label_visibility="collapsed", key="input_text")
with b4:
    send = st.button("➤", use_container_width=True, type="primary")

if (send or q) and q and q.strip()!="":
    # envoie
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
