import streamlit as st, requests, base64, json, os, uuid
from datetime import datetime

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
.stApp {background:#fcfaf8!important;}
section[data-testid="stSidebar"] {background:#f5f2ed!important; width:300px!important;}
div[data-testid="stChatMessages"] {max-width:760px; margin:0 auto;}
.stChatMessage p {font-size:15px!important; line-height:1.7!important;}
</style>
""", unsafe_allow_html=True)

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]

FILE = "angel_final.json"
def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"conversations": [], "active_id": None}

def save():
    with open(FILE,"w",encoding="utf-8") as f: json.dump(st.session_state.data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state: st.session_state.data = load()
if "active_classe" not in st.session_state: st.session_state.active_classe = "3e"

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def call_angel(q, classe, img=None):
    if img:
        b64 = base64.b64encode(img).decode()
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[
                {"role":"system","content":f"Tu es Angel, prof de {classe}"},
                {"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
            ]}, timeout=60).json()
    else:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={"model":"openai/gpt-oss-20b","messages":[
                {"role":"system","content":f"Tu es Angel, prof de {classe}. Programme strict {classe}."},
                {"role":"user","content":q}]}, timeout=30).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur"

def new_conv(classe):
    cid = str(uuid.uuid4())[:8]
    conv = {"id":cid, "title":f"Nouvelle conversation - {classe}", "classe":classe, "messages":[], "date":datetime.now().strftime("%d/%m %H:%M")}
    st.session_state.data["conversations"].insert(0, conv)
    st.session_state.data["active_id"] = cid
    save()

def get_active():
    aid = st.session_state.data["active_id"]
    for c in st.session_state.data["conversations"]:
        if c["id"] == aid: return c
    return None

# --- SIDEBAR COMME CHATGPT ---
with st.sidebar:
    st.markdown("## 🕊️ Angel")

    if st.button("➕ Nouvelle conversation", use_container_width=True, type="primary"):
        new_conv(st.session_state.active_classe)
        st.rerun()

    st.markdown("---")
    st.markdown("**📚 Choisir la classe**")
    sel = st.selectbox("Classe active", CLASSES, index=CLASSES.index(st.session_state.active_classe), label_visibility="collapsed")
    st.session_state.active_classe = sel
    st.caption(f"Salle: {sel}")

    st.markdown("---")
    st.markdown("**🎙️📸 Outils**")
    up = st.file_uploader("📸 Photo / Fichier", type=["jpg","png","jpeg","pdf"], label_visibility="collapsed")
    cam = st.camera_input("Caméra", label_visibility="collapsed")
    aud = st.audio_input("🎙️ Message vocal", label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**💬 Anciennes conversations**")
    if not st.session_state.data["conversations"]:
        st.caption("Aucune conversation")
    else:
        for conv in st.session_state.data["conversations"][:20]:
            is_active = conv["id"] == st.session_state.data["active_id"]
            label = f"{'🔵' if is_active else '⚪'} {conv['title'][:22]} | {conv['classe']} | {conv['date']}"
            if st.button(label, key=f"conv_{conv['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.data["active_id"] = conv["id"]
                st.session_state.active_classe = conv["classe"]
                st.rerun()

# --- MAIN ---
active_conv = get_active()

if not active_conv:
    st.markdown(f"""
    <div style='max-width:760px; margin:80px auto; text-align:center;'>
        <h1>🕊️ Angel</h1>
        <p>Bienvenue! Choisis une classe et clique sur <b>Nouvelle conversation</b></p>
        <p>📚 {', '.join(CLASSES[:6])}... jusqu'à Doctorat</p>
        <p>🎙️ Vocal • 📸 Photo • 💾 Mémoire automatique</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"#### 🕊️ {active_conv['title']} • Salle {active_conv['classe']} • {len(active_conv['messages'])} messages")

    for m in active_conv["messages"]:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Traitements
    img_bytes = None
    if cam: img_bytes = cam.getvalue()
    elif up and hasattr(up,'getvalue'): img_bytes = up.getvalue()

    if img_bytes and st.button(f"📸 Analyser avec Angel {active_conv['classe']}"):
        ans = call_angel("Résous cet exercice étape par étape", active_conv["classe"], img_bytes)
        active_conv["messages"].extend([{"role":"user","content":"📸 [Photo envoyée]"},{"role":"assistant","content":ans}])
        if len(active_conv["messages"]) == 2: active_conv["title"] = f"Photo - {active_conv['classe']}"
        save(); st.rerun()

    if aud:
        # transcription simple
        files={"file":("a.wav", aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
        try:
            r=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json()
            txt = r.get("text","")
            if txt:
                active_conv["messages"].append({"role":"user","content":f"🎙️ {txt}"})
                ans = call_angel(txt, active_conv["classe"])
                active_conv["messages"].append({"role":"assistant","content":ans})
                save(); st.rerun()
        except: pass

    q = st.chat_input(f"Écris à Angel en {active_conv['classe']}...")
    if q:
        active_conv["messages"].append({"role":"user","content":q})
        if len(active_conv["messages"]) == 1: active_conv["title"] = q[:30]
        ans = call_angel(q, active_conv["classe"])
        active_conv["messages"].append({"role":"assistant","content":ans})
        save(); st.rerun()
