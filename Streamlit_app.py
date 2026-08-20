import streamlit as st, requests
st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("<style>.stApp{background:#0a0d13;color:#edeff3;} section[data-testid='stSidebar']{background:#10141c;}</style>", unsafe_allow_html=True)

LEVELS=["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Master 1","Master 2"]
if "messages" not in st.session_state: st.session_state.messages=[]
if "level" not in st.session_state: st.session_state.level="Terminale"

def call_groq(q, key, level):
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {key}"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":f"Tu es Angel, prof niveau {level}. Direct, dense."},{"role":"user","content":q}]},
        timeout=30)
    return r.json()["choices"][0]["message"]["content"]

with st.sidebar:
    st.markdown("### 🕊️ Angel - Rapide")
    st.session_state.level=st.selectbox("Niveau",LEVELS, index=6)
    groq_key=st.text_input("Clé Groq gsk_...", type="password", help="Gratuit sur groq.com")
    st.caption("Groq = gratuit, sans CB, 1 sec de réponse")
    if st.button("Effacer"): st.session_state.messages=[]; st.rerun()

st.title("🕊️ Angel")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.write(m["content"])

q=st.chat_input("Ta question…")
if q:
    if not groq_key: st.error("Mets ta clé Groq gsk_... dans la sidebar")
    else:
        st.session_state.messages.append({"role":"user","content":q})
        with st.chat_message("user"): st.write(q)
        with st.spinner("..."):
            ans=call_groq(q, groq_key, st.session_state.level)
        st.session_state.messages.append({"role":"assistant","content":ans})
        with st.chat_message("assistant"): st.write(ans)
