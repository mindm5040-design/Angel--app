import requests
import streamlit as st
import urllib.parse

st.set_page_config(page_title="Angel - Gratuit", page_icon="🕊️", layout="wide")
st.markdown("<style>.stApp{background:#0a0d13;color:#edeff3;} section[data-testid='stSidebar']{background:#10141c;}</style>", unsafe_allow_html=True)

LEVELS = ["6e", "5e", "4e", "3e", "Seconde", "Première", "Terminale", "Licence 1", "Licence 2", "Master 1", "Master 2"]
if "level" not in st.session_state: st.session_state.level = "Terminale"
if "messages" not in st.session_state: st.session_state.messages = []

def call_free_ai(question, level):
    # IA 100% gratuite, sans clé, illimitée - via Pollinations
    system = f"Tu es Angel, instrument d'étude académique niveau {level}. Réponse directe, dense, pédagogique. Exclusivement scolaire."
    full_prompt = f"{system}\n\nQuestion: {question}"
    encoded = urllib.parse.quote(full_prompt)
    r = requests.get(f"https://text.pollinations.ai/{encoded}?model=openai", timeout=60)
    if r.status_code != 200:
        raise RuntimeError(r.text[:300])
    return r.text.strip()

with st.sidebar:
    st.markdown(f"### 🕊️ Angel\n**Gratuit - Sans clé**")
    st.session_state.level = st.selectbox("Ton niveau", LEVELS, index=4)
    if st.button("Effacer la conversation"): st.session_state.messages=[]; st.rerun()
    st.success("✅ Aucune clé requise\nIllimité et gratuit")

st.title("🕊️ Angel")
st.caption(f"Mode gratuit • Niveau {st.session_state.level} • Llama 3.3 70B")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.write(m["content"])

q = st.chat_input("Ta question de cours…")
if q:
    st.session_state.messages.append({"role":"user","content":q})
    with st.chat_message("user"): st.write(q)
    with st.spinner("Angel réfléchit…"):
        try:
            ans = call_free_ai(q, st.session_state.level)
            st.session_state.messages.append({"role":"assistant","content":ans})
            with st.chat_message("assistant"): st.write(ans)
        except Exception as e:
            st.error(f"Erreur: {e} - Réessaie")
