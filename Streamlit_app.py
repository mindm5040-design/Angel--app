import streamlit as st
import requests
import os

st.set_page_config(page_title="Angel AI", page_icon="🧬", layout="centered")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")

KEY = get_key()

st.markdown("""
<style>
.stApp{background:#FCFCF9!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
</style>
""", unsafe_allow_html=True)

st.title("Angel AI 🧬")
st.caption("DNA REPLICATION - ACTIVE")

if not KEY:
    st.warning("Ajoute ta cle GROQ dans Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_groq(q):
    try:
        data = {
            "model":"openai/gpt-oss-20b",
            "messages":[
                {"role":"system","content":"Tu es Angel, prof bienveillante niveau Doctorat. Tu expliques clairement en francais."},
                {"role":"user","content":q}
            ]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers={"Authorization": f"Bearer {KEY}"},
                          json=data, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur: {e}"

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Question niveau Doctorat...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ans = ask_groq(prompt)
    st.session_state.messages.append({"role":"assistant","content":ans})
    with st.chat_message("assistant"):
        st.markdown(ans)
