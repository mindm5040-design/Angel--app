import streamlit as st, requests

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:wght@400;500&display=swap');
.stApp {background:#fcfaf8!important;}
section[data-testid="stSidebar"] {background:#f5f2ed!important;}
div[data-testid="stSidebar"] button {font-size:13px!important; padding:8px 12px!important;}

/* CHAT LISIBLE MAIS PAS GROS */
div[data-testid="stChatMessages"] {max-width:760px; margin:0 auto; gap:1.2rem!important; padding-bottom:40px!important;}
.stChatMessage {background:transparent!important; border:none!important; padding:8px!important;}
.stChatMessage p,.stChatMessage li {
    font-family:'Source Serif 4', serif!important;
    font-size:15.5px!important;
    line-height:1.7!important;
    color:#1a1a1a!important;
}
.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:18px!important; padding:12px 16px!important; font-family:'Inter', sans-serif!important;
}

/* INPUT BIEN VISIBLE */
div[data-testid="stChatInput"] {
    max-width:760px; margin:0 auto; background:white!important;
    border:1px solid #e8e0d0!important; border-radius:24px!important;
    box-shadow:0 2px 12px rgba(0,0,0,0.06)!important;
}
</style>
""", unsafe_allow_html=True)

# --- TOUTES LES CLASSES ---
CLASSES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
}

if "class_chats" not in st.session_state:
    st.session_state.class_chats = {c: [] for v in CLASSES.values() for c in v}
if "active_classe" not in st.session_state:
    st.session_state.active_classe = "3e"

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def call_angel(q, classe):
    sys = f"Tu es Angel, prof de {classe}. Programme strict {classe}. Réponse claire, aérée, 15px, pas trop longue. Français."
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":sys},{"role":"user","content":q}]}, timeout=30).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e: return f"Erreur: {e}"

# --- SIDEBAR AVEC TOUTES LES CLASSES ---
with st.sidebar:
    st.markdown("## 🕊️ Angel")
    st.caption(f"Salle active: **{st.session_state.active_classe}**")

    for cycle, liste in CLASSES.items():
        st.markdown(f"**{cycle}**")
        cols = st.columns(2)
        for i, c in enumerate(liste):
            is_active = st.session_state.active_classe == c
            with cols[i % 2]:
                if st.button(f"{'🔵' if is_active else ''} {c}", key=f"btn_{c}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state.active_classe = c
                    st.rerun()
        st.markdown("")

    st.markdown("---")
    st.file_uploader("📸 Photo", type=["jpg","png","jpeg"], key="up")
    if st.button("🗑️ Vider cette salle", use_container_width=True):
        st.session_state.class_chats[st.session_state.active_classe] = []
        st.rerun()

# --- CHAT ---
active = st.session_state.active_classe
st.markdown(f"<div style='max-width:760px; margin:0 auto; padding:10px;'><span style='background:#1a1a1a; color:white; padding:6px 14px; border-radius:20px; font-size:13px;'>🕊️ Angel • {active}</span> <span style='color:#888; font-size:13px; margin-left:8px;'>🔒 Programme {active} uniquement</span></div>", unsafe_allow_html=True)

for m in st.session_state.class_chats[active]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input(f"Écris à Angel en {active}... ( + photo 🎙️ dans le menu )")

if q:
    st.session_state.class_chats[active].append({"role":"user","content":q})
    ans = call_angel(q, active)
    st.session_state.class_chats[active].append({"role":"assistant","content":ans})
    st.rerun()
