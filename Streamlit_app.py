import streamlit as st, requests, base64

st.set_page_config(page_title="Angel Pro", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');
* {font-family:'Inter', sans-serif;}
.stApp {background:#0f0f10; color:#ececec;}
section[data-testid="stSidebar"] {background:#18181b; border-right:1px solid #27272a;}
div[data-testid="stChatMessages"] {gap: 1.6rem!important; padding-top: 2rem; padding-bottom: 4rem;}
.stChatMessage {
    background:#18181b!important;
    border:1px solid #27272a!important;
    border-radius:20px!important;
    padding: 24px 28px!important;
    max-width: 820px!important;
    margin: 0 auto!important;
}
.stChatMessage p,.stChatMessage li {
    font-family:'Source Serif 4', serif!important;
    font-size: 17px!important;
    line-height: 1.85!important;
    letter-spacing: 0.2px!important;
    color: #f4f4f5!important;
}
.stChatMessage h1,.stChatMessage h2,.stChatMessage h3 {
    font-family:'Inter', sans-serif!important;
    font-weight:600!important;
    color:#fff!important;
    margin-top: 1.2em!important;
}
div[data-testid="stChatInput"] {
    background:#18181b!important;
    border:1px solid #3f3f46!important;
    border-radius:24px!important;
    max-width: 820px!important;
    margin: 0 auto!important;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "niveau" not in st.session_state: st.session_state.niveau = "Terminale"
if "cycle" not in st.session_state: st.session_state.cycle = "Lycée"

KEY = st.secrets.get("GROQ_API_KEY","").strip()
CYCLES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
}
PROGRAMMES = {
    "6e": "bases fractions, décimaux, géométrie simple", "5e": "fractions, proportionnalité", "4e": "Pythagore, Thalès, équations",
    "3e": "fonctions, racine carrée, Brevet", "Seconde": "fonctions, vecteurs", "Première": "dérivées, suites",
    "Terminale": "limites, intégrales, Bac", "Licence 1": "analyse réelle, algèbre linéaire", "Licence 2": "analyse avancée",
    "Licence 3": "topologie", "Master 1": "master recherche", "Master 2": "expert", "Doctorat": "recherche doctorale"
}

def call_text(q, niveau, cycle):
    prog = PROGRAMMES.get(niveau, "")
    sys = f"Tu es Angel, prof d'élite {cycle} {niveau}. Programme: {prog}. RÈGLE: reste STRICTEMENT en {niveau}. Si hors programme, refuse poliment. Réponse en français clair, aérée, avec titres et exemples. Niveau {niveau}."
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":sys},{"role":"user","content":q}]}, timeout=40).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur: {r}"

def call_vision(q, img_bytes, niveau):
    b64 = base64.b64encode(img_bytes).decode()
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[
            {"role":"system","content":f"Prof {niveau}. Analyse image."},
            {"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
        ]}, timeout=60).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur vision: {r}"

def transcribe(b):
    try:
        files = {"file": ("a.wav", b, "audio/wav")}; data = {"model":"whisper-large-v3","language":"fr"}
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json()
        return r.get("text","")
    except: return ""

with st.sidebar:
    st.markdown("## 🕊️ Angel Pro")
    cycle = st.segmented_control("Cycle", list(CYCLES.keys()), default=st.session_state.cycle)
    if cycle: st.session_state.cycle = cycle
    niveau = st.segmented_control("Niveau", CYCLES[st.session_state.cycle], default=st.session_state.niveau if st.session_state.niveau in CYCLES[st.session_state.cycle] else CYCLES[st.session_state.cycle][0])
    if niveau: st.session_state.niveau = niveau
    st.markdown("---")
    st.caption(f"🔒 Verrouillé sur {st.session_state.niveau}")
    st.file_uploader("📸 Photo exo", type=["jpg","png","jpeg"], key="up")
    st.camera_input("Caméra", key="cam", label_visibility="collapsed")
    st.audio_input("🎙️ Vocal", key="aud", label_visibility="collapsed")
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages=[]; st.rerun()

st.markdown(f"### 🕊️ Angel • {st.session_state.cycle} — {st.session_state.niveau}")
st.caption("Texte aéré • Lecture confortable comme Claude")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Photo
img = st.session_state.get("cam") or st.session_state.get("up")
if img and st.session_state.get("up") is not None or st.session_state.get("cam") is not None:
    if st.button("📸 Analyser la photo"):
        ans = call_vision("Résous l'exercice sur l'image étape par étape", img.getvalue(), st.session_state.niveau)
        st.session_state.messages.append({"role":"user","content":"📸 [Photo d'exercice]"})
        st.session_state.messages.append({"role":"assistant","content":ans}); st.rerun()

# Vocal
aud = st.session_state.get("aud")
if aud:
    txt = transcribe(aud.getvalue())
    if txt:
        st.session_state.messages.append({"role":"user","content":f"🎙️ {txt}"})
        ans = call_text(txt, st.session_state.niveau, st.session_state.cycle)
        st.session_state.messages.append({"role":"assistant","content":ans}); st.rerun()

q = st.chat_input(f"Question de {st.session_state.niveau}...")
if q:
    st.session_state.messages.append({"role":"user","content":q})
    ans = call_text(q, st.session_state.niveau, st.session_state.cycle)
    st.session_state.messages.append({"role":"assistant","content":ans}); st.rerun()
