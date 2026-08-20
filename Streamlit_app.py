import streamlit as st, requests
st.set_page_config(page_title="Angel", page_icon="🕊️")
if "m" not in st.session_state: st.session_state.m=[]
KEY=st.secrets.get("GROQ_API_KEY","").strip()
st.title("🕊️ Angel")
if not KEY:
    st.error("Clé manquante dans Secrets")
    st.stop()
for x in st.session_state.m:
    with st.chat_message(x["r"]): st.write(x["c"])
q=st.chat_input("Ta question...")
if q:
    st.session_state.m.append({"r":"user","c":q})
    with st.chat_message("user"): st.write(q)
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json={"model":"llama-3.1-8b-instant","messages":[{"role":"user","content":q}]}, timeout=30).json()
        ans=r["choices"][0]["message"]["content"] if "choices" in r else f"Erreur: {r}"
    except Exception as e:
        ans=f"Erreur: {e}"
    st.session_state.m.append({"r":"assistant","c":ans})
    with st.chat_message("assistant"): st.write(ans)
