import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:0 auto; padding-bottom:20px!important; gap:4px!important;}
.stChatMessage p {font-size:15.5px!important; line-height:1.7!important;}
div[data-testid="stChatInput"] {
    max-width:720px; margin:0 auto; background:#f5f5f5!important;
    border:1px solid #e5e5e5!important; border-radius:24px!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px 18px 4px 18px!important; padding:10px 14px!important;
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
if "show_tools" not in st.session_state: st.session_state.show_tools = False

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

# --- HEADER SOIGNÉ ---
st.markdown(f"<div style='max-width:720px; margin:0 auto; padding:8px 0;'><b>🕊️ Angel • {cl}</b> <span style='color:#888; font-size:12px;'>• {len(st.session_state.chats[cl])} messages</span></div>", unsafe_allow_html=True)

# --- BARRE D'OUTILS COMPACTE (au lieu des gros blocs) ---
t1, t2, t3, t4 = st.columns([2,1,1,1])
with t1:
    new_cl = st.selectbox("Classe", CLASSES, index=CLASSES.index(cl), label_visibility="collapsed")
    if new_cl!= cl:
        st.session_state.classe = new_cl; st.rerun()
with t2:
    if st.button("📷", use_container_width=True): st.session_state.show_tools = "photo" if st.session_state.show_tools!= "photo" else False; st.rerun()
with t3:
    if st.button("🎙️", use_container_width=True): st.session_state.show_tools = "vocal" if st.session_state.show_tools!= "vocal" else False; st.rerun()
with t4:
    if st.button("🗑️", use_container_width=True):
        st.session_state.chats[cl]=[]; save(); st.rerun()

# --- LES GROS BLOCS S'AFFICHENT UNIQUEMENT SI ON CLIQUE ---
img_data = None
if st.session_state.show_tools == "photo":
    st.markdown("<div style='background:#fafafa; border:1px solid #eee; border-radius:12px; padding:12px;'>", unsafe_allow_html=True)
    up = st.file_uploader("Importer une photo", type=["jpg","png"], label_visibility="collapsed")
    cam = st.camera_input("Prendre", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    if cam: img_data = cam.getvalue()
    elif up and hasattr(up,'getvalue'): img_data = up.getvalue()
    if img_data and st.button(f"Analyser en {cl}", use_container_width=True, type="primary"):
        ans = ask(f"Résous niveau {cl}", cl, img_data)
        st.session_state.chats[cl].extend([{"role":"user","content":"📷 Photo"},{"role":"assistant","content":ans}])
        st.session_state.show_tools = False; save(); st.rerun()

if st.session_state.show_tools == "vocal":
    st.markdown("<div style='background:#fafafa; border:1px solid #eee; border-radius:12px; padding:12px;'>", unsafe_allow_html=True)
    aud = st.audio_input("Vocal", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    if aud:
        try:
            files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
            txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
            if txt:
                st.session_state.chats[cl].append({"role":"user","content":txt})
                st.session_state.chats[cl].append({"role":"assistant","content":ask(txt, cl)})
                st.session_state.show_tools = False; save(); st.rerun()
        except: pass

# --- CHAT ---
for m in st.session_state.chats[cl]:
    with st.chat_message(m["role"]): st.markdown(m["content"])

q = st.chat_input(f"Écris à Angel en {cl}...")
if q:
    st.session_state.chats[cl].append({"role":"user","content":q})
    st.session_state.chats[cl].append({"role":"assistant","content":ask(q, cl)})
    save(); st.rerun()
