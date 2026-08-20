import streamlit as st, requests, base64, json, os, re
from datetime import datetime

st.set_page_config(page_title="Angel • ChatGPT + Claude", page_icon="🕊️", layout="wide")

# --- CSS CHATGPT + CLAUDE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
.stApp {background:#ffffff!important;}
section[data-testid="stSidebar"] {background:#f9f9f7!important; border-right:1px solid #e5e5e5;}
div[data-testid="stChatMessages"] {max-width:800px; margin:0 auto;}
.stChatMessage p {font-size:15px!important; line-height:1.75!important;}
button[kind="secondary"] {font-size:12.5px!important;}
</style>
""", unsafe_allow_html=True)

CLASSES = {
    "Collège": ["6e","5e","4e","3e"],
    "Lycée": ["Seconde","Première","Terminale"],
    "Université": ["Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
}
ALL = [c for v in CLASSES.values() for c in v]

MODELS = {
    "Angel Rapide (comme Haiku)": "openai/gpt-oss-20b",
    "Angel Intelligent (comme Sonnet 4.5)": "openai/gpt-oss-120b",
    "Angel Vision (Photos)": "meta-llama/llama-4-scout-17b-16e-instruct"
}

FILE = "angel_memory_v8.json"
def load_mem():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {c: [] for c in ALL}

def save_mem():
    with open(FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.chats, f, ensure_ascii=False, indent=2)

if "chats" not in st.session_state: st.session_state.chats = load_mem()
if "active" not in st.session_state: st.session_state.active = "Terminale"
if "model" not in st.session_state: st.session_state.model = "Angel Rapide (comme Haiku)"
if "artefact" not in st.session_state: st.session_state.artefact = ""

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def call_angel(prompt, classe, model_name, with_search=False):
    model_id = MODELS[model_name]
    sys = f"""Tu es Angel, IA d'élite niveau {classe}. Tu combines ChatGPT et Claude.
- Programme STRICT {classe}. Si hors programme, refuse poliment.
- Si tu écris du code, mets-le entre ``` et explique.
- Si c'est un document long, mets [ARTEFACT] ton contenu [/ARTEFACT] à la fin.
- Français clair, structuré avec titres.
- Date: {datetime.now().strftime('%d/%m/%Y')}"""

    if with_search:
        prompt = f"[Recherche web activée] {prompt}"

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model": model_id, "messages":[{"role":"system","content":sys},{"role":"user","content":prompt}]}, timeout=40).json()

    text = r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur: {r}"

    # Extraire artefact comme Claude
    m = re.search(r"\[ARTEFACT\](.*?)\[/ARTEFACT\]", text, re.DOTALL)
    if m:
        st.session_state.artefact = m.group(1).strip()
        text = text.replace(m.group(0), "\n\n> 📄 **Artefact créé à droite →**")
    return text

def vision(q, img, classe):
    b64 = base64.b64encode(img).decode()
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model": MODELS["Angel Vision (Photos)"],"messages":[
            {"role":"system","content":f"Prof {classe}"},
            {"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
        ]}, timeout=60).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur vision"

def transcribe(b):
    try:
        files={"file":("a.wav",b,"audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
        r=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json()
        return r.get("text","")
    except: return ""

# --- SIDEBAR = CHATGPT + CLAUDE ---
with st.sidebar:
    st.markdown("## 🕊️ Angel")
    st.selectbox("Modèle (comme Claude)", list(MODELS.keys()), key="model")
    st.toggle("🌐 Recherche Web", key="search")
    st.toggle("🧠 Raisonnement Étendu", key="extended")

    st.markdown("---")
    st.markdown("**Salles de classe**")
    for cycle, liste in CLASSES.items():
        st.caption(cycle)
        c1,c2 = st.columns(2)
        for i,c in enumerate(liste):
            with [c1,c2][i%2]:
                if st.button(f"{'🔵' if st.session_state.active==c else '⚪'} {c}", key=f"s_{c}", use_container_width=True, type="primary" if st.session_state.active==c else "secondary"):
                    st.session_state.active=c; st.rerun()

    st.markdown("---")
    st.file_uploader("📎 Fichier / Photo", type=["jpg","png","pdf","docx"], key="up")
    st.camera_input("📸", label_visibility="collapsed", key="cam")
    st.audio_input("🎙️ Vocal", label_visibility="collapsed", key="aud")

    if st.button("🗑️ Vider salle", use_container_width=True):
        st.session_state.chats[st.session_state.active]=[]; save_mem(); st.rerun()
    if st.button("💾 Exporter chat", use_container_width=True):
        st.download_button("Télécharger", json.dumps(st.session_state.chats[st.session_state.active], ensure_ascii=False, indent=2), file_name=f"Angel_{st.session_state.active}.json")

# --- LAYOUT CHATGPT + CLAUDE ARTEFACT ---
col_chat, col_art = st.columns([1.2, 0.8] if st.session_state.artefact else [1,0])

with col_chat:
    active = st.session_state.active
    st.markdown(f"### Salle {active} • {st.session_state.model} {'• Étendu' if st.session_state.get('extended') else ''}")

    for i,m in enumerate(st.session_state.chats[active]):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"]=="assistant":
                b1,b2,b3 = st.columns([1,1,4])
                with b1:
                    if st.button("📋 Copier", key=f"cp_{i}"): st.toast("Copié!")
                with b2:
                    if st.button("🔄 Régénérer", key=f"re_{i}"):
                        last_user = st.session_state.chats[active][i-1]["content"] if i>0 else ""
                        new = call_angel(last_user, active, st.session_state.model, st.session_state.get("search",False))
                        st.session_state.chats[active][i]["content"]=new; save_mem(); st.rerun()

    # Inputs
    img = st.session_state.get("cam") or st.session_state.get("up")
    if img and hasattr(img, 'getvalue') and st.button("Analyser"):
        ans = vision("Explique", img.getvalue(), active)
        st.session_state.chats[active].extend([{"role":"user","content":"📸 [Image]"},{"role":"assistant","content":ans}]); save_mem(); st.rerun()

    aud = st.session_state.get("aud")
    if aud:
        txt = transcribe(aud.getvalue())
        if txt:
            st.session_state.chats[active].append({"role":"user","content":f"🎙️ {txt}"})
            ans = call_angel(txt, active, st.session_state.model, st.session_state.get("search",False))
            st.session_state.chats[active].append({"role":"assistant","content":ans}); save_mem(); st.rerun()

    q = st.chat_input(f"Message à Angel en {active}... (+ pour fichier)")
    if q:
        st.session_state.chats[active].append({"role":"user","content":q})
        ans = call_angel(q, active, st.session_state.model, st.session_state.get("search",False))
        st.session_state.chats[active].append({"role":"assistant","content":ans}); save_mem(); st.rerun()

with col_art:
    if st.session_state.artefact:
        st.markdown("#### 📄 Artefact - comme Claude")
        st.code(st.session_state.artefact, language="python")
        st.download_button("⬇️ Télécharger artefact", st.session_state.artefact, file_name="artefact_angel.txt")
        if st.button("✕ Fermer artefact"): st.session_state.artefact=""; st.rerun()
