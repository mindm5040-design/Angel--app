import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:80px!important;}
.stChatMessage p {font-size:15.5px!important; line-height:1.75!important; font-family:'Source Serif 4', serif!important;}
div[data-testid="stChatInput"] {
    max-width:720px; margin:0 auto;
    border:1px solid #e5e5e5!important; border-radius:24px!important;
    background:#f5f5f5!important; box-shadow:none!important;
}
div[data-testid="stChatInput"] textarea {background:#f5f5f5!important;}
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

# --- HEADER COMME TA CAPTURE ---
cl = st.session_state.classe
st.markdown(f"""
<div style='max-width:720px; margin:0 auto; padding:12px 4px; display:flex; align-items:center; gap:8px;'>
    <span style='font-size:20px;'>🕊️</span>
    <span style='font-weight:600; font-size:17px;'>Angel • {cl}</span>
    <span style='color:#888; font-size:13px;'>• {len(st.session_state.chats[cl])} messages sauvegardés</span>
</div>
""", unsafe_allow_html=True)

# --- SELECTEUR DE CLASSES - TON DESIGN ---
with st.expander("📚 Changer de classe - 6e → Doctorat", expanded=False):
    c1,c2,c3 = st.columns(3)
    for i, classe in enumerate(CLASSES):
        with [c1,c2,c3][i%3]:
            if st.button(classe, key=f"cl_{classe}", use_container_width=True, type="primary" if classe==cl else "secondary"):
                st.session_state.classe = classe
                st.rerun()
    st.markdown("---")
    up = st.file_uploader("📸 Photo d'exercice", type=["jpg","png","jpeg"])
    cam = st.camera_input("📸 Caméra")
    aud = st.audio_input("🎙️ Vocal")

# --- CHAT ---
for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Photo
img_data = None
if 'cam' in locals() and cam: img_data = cam.getvalue()
elif 'up' in locals() and up and hasattr(up,'getvalue'): img_data = up.getvalue()

if img_data:
    if st.button(f"📸 Analyser en {cl}", use_container_width=True):
        ans = ask(f"Résous niveau {cl}", cl, img_data)
        st.session_state.chats[cl].extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":ans}])
        save(); st.rerun()

if 'aud' in locals() and aud:
    try:
        files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
        txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
        if txt:
            st.session_state.chats[cl].append({"role":"user","content":f"🎙️ {txt}"})
            st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)})
            save(); st.rerun()
    except: pass

q = st.chat_input(f"Écris à Angel en {cl}...")
if q:
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
