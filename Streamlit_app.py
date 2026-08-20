import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
.stApp {background:#fcfaf8!important;}
div[data-testid="stChatMessages"] {max-width:760px; margin:0 auto; padding-bottom:80px!important;}
.stChatMessage p {font-size:15px!important; line-height:1.7!important;}
div[data-testid="stChatInput"] {max-width:760px; margin:0 auto; border-radius:24px!important; background:white!important; border:1px solid #e5ddd5!important;}
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

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def ask(q, classe, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}"},{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof de {classe}. Programme strict {classe}."},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=40).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur"

# --- BARRE DE CLASSES VISIBLE MEME SUR MOBILE ---
st.markdown("### 🕊️ Angel")
cols = st.columns(4)
for i, cl in enumerate(CLASSES):
    with cols[i%4]:
        if st.button(cl, key=f"m_{cl}", use_container_width=True, type="primary" if cl==st.session_state.classe else "secondary"):
            st.session_state.classe = cl
            st.rerun()

# --- OUTILS VISIBLES EN HAUT AUSSI ---
with st.expander("📸🎙️ Photo & Vocal - Clique ici", expanded=False):
    up = st.file_uploader("Photo", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam = st.camera_input("Caméra", label_visibility="collapsed")
    aud = st.audio_input("Vocal", label_visibility="collapsed")
    if st.button("🗑️ Vider cette salle"):
        st.session_state.chats[st.session_state.classe]=[]; save(); st.rerun()
else:
    up = None; cam = None; aud = None

# --- SIDEBAR AUSSI POUR PC ---
with st.sidebar:
    st.markdown("## 🕊️ Angel")
    st.caption("Clique sur >> en haut à gauche sur mobile")
    up2 = st.file_uploader("📸 Photo PC", type=["jpg","png"], label_visibility="collapsed", key="up2")
    cam2 = st.camera_input("Caméra PC", label_visibility="collapsed", key="cam2")
    aud2 = st.audio_input("Vocal PC", label_visibility="collapsed", key="aud2")
    if up2: up = up2
    if cam2: cam = cam2
    if aud2: aud = aud2

# --- CHAT ---
cl = st.session_state.classe
st.markdown(f"**Angel • {cl} • {len(st.session_state.chats[cl])} messages**")

for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

img_data = cam.getvalue() if cam and hasattr(cam,'getvalue') else (up.getvalue() if up and hasattr(up,'getvalue') else None)

if img_data and st.button(f"📸 Analyser en {cl}", use_container_width=True):
    ans = ask(f"Résous niveau {cl}", cl, img_data)
    st.session_state.chats[cl].extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":ans}]); save(); st.rerun()

if aud:
    try:
        files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
        txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
        if txt:
            st.session_state.chats[cl].append({"role":"user","content":f"🎙️ {txt}"})
            st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)}); save(); st.rerun()
    except: pass

q = st.chat_input(f"Écris à Angel en {cl}...")
if q:
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
