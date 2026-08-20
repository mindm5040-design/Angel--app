import streamlit as st, requests

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:wght@400;600&display=swap');
.stApp {background:#fcfaf8!important; color:#1a1a1a!important;}
section[data-testid="stSidebar"] {background:#f5f2ed!important;}
div[data-testid="stChatMessages"] {gap:1.8rem!important; padding-bottom:120px!important; max-width:800px; margin:0 auto;}
.stChatMessage p {font-family:'Source Serif 4', serif!important; font-size:18px!important; line-height:1.9!important; color:#1a1a1a!important;}
.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; border-radius:20px 20px 4px 20px!important; padding:16px 20px!important;
}
.classe-btn {width:100%; text-align:left; padding:12px 14px; border-radius:12px; border:1px solid #e8e0d0; background:white; margin-bottom:8px; cursor:pointer;}
.classe-btn-active {background:#1a1a1a!important; color:white!important; border-color:#1a1a1a!important;}
</style>
""", unsafe_allow_html=True)

# --- INIT SALLES ---
CLASSES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["Licence 1", "Licence 2", "Licence 3", "Master 1"]
}

if "class_chats" not in st.session_state:
    st.session_state.class_chats = {classe: [] for cycle in CLASSES.values() for classe in cycle}
if "active_classe" not in st.session_state:
    st.session_state.active_classe = "Terminale"

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def call_angel(q, classe):
    sys = f"Tu es Angel, prof officiel de la classe {classe}. Tu ne fais QUE le programme de {classe}. Reste strictement bloqué en {classe}. Réponse très lisible, titres, exemples. En français."
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":sys},{"role":"user","content":q}]}, timeout=30).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur: {r}"

# --- SIDEBAR: SALLES DE CLASSE ---
with st.sidebar:
    st.markdown("## 🕊️ Angel")
    st.caption("Choisis ta salle de classe")

    for cycle, classes in CLASSES.items():
        st.markdown(f"**{cycle}**")
        for c in classes:
            is_active = st.session_state.active_classe == c
            label = f"{'🔵' if is_active else '⚪'} {c} - {len(st.session_state.class_chats[c])} messages"
            if st.button(label, key=f"btn_{c}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.active_classe = c
                st.rerun()
        st.markdown("")

    st.markdown("---")
    st.file_uploader("📸 Photo d'exo", type=["jpg","png"], key="up")
    st.audio_input("🎙️ Vocal", key="aud")

# --- MAIN: CHAT DE LA CLASSE ACTIVE ---
active = st.session_state.active_classe
st.markdown(f"""
<div style='max-width:800px; margin:0 auto; padding:10px 20px;'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <h2 style='margin:0;'>🕊️ Angel • Salle {active}</h2>
        <span style='background:#1a1a1a; color:white; padding:6px 12px; border-radius:20px; font-size:13px;'>🔒 {active}</span>
    </div>
    <p style='color:#6b6b6b;'>Bienvenue dans la salle {active}. Angel ne répond que dans ce programme.</p>
</div>
""", unsafe_allow_html=True)

# Afficher les messages de CETTE salle uniquement
for m in st.session_state.class_chats[active]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input
q = st.chat_input(f"Répondre à Angel en {active}...")

# Barre du bas style Claude comme ta capture verte
st.markdown(f"""
<div style='position:fixed; bottom:0; left:0; right:0; background:#fcfaf8; border-top:1px solid #e8e0d0; padding:12px; display:flex; justify-content:center; z-index:999;'>
  <div style='width:100%; max-width:780px; background:white; border:1px solid #e8e0d0; border-radius:28px; padding:10px 12px; display:flex; gap:10px; align-items:center;'>
    <div style='width:36px; height:36px; border-radius:50%; background:#f0ece2; display:flex; align-items:center; justify-content:center;'>+</div>
    <div style='flex:1; background:#f0ece2; border-radius:20px; padding:8px; text-align:center; font-size:14px;'>Angel {active} • Étendu</div>
    <div style='width:36px; height:36px; border-radius:50%; background:#f0ece2; display:flex; align-items:center; justify-content:center;'>🎙️</div>
    <div style='width:40px; height:40px; border-radius:50%; background:#1a1a1a; color:white; display:flex; align-items:center; justify-content:center;'>🔊</div>
  </div>
</div>
""", unsafe_allow_html=True)

if q:
    st.session_state.class_chats[active].append({"role":"user","content":q})
    ans = call_angel(q, active)
    st.session_state.class_chats[active].append({"role":"assistant","content":ans})
    st.rerun()
