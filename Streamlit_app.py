import streamlit as st, requests
st.set_page_config(page_title="Angel", page_icon="🕊️")
if "m" not in st.session_state: st.session_state.m=[]
KEY=st.secrets.get("GROQ_API_KEY","").strip()
st.title("🕊️ Angel")
if not KEY:
    st.error("Va dans Manage app > Settings > Secrets et mets: GROQ_API_KEY = \"gsk_...\"")
    st.stop()
for x in st.session_state.m:
    with st.chat_message(x["r"]): st.write(x["c"])
q=st.chat_input("Ta question...")
if q:
    st.session_state.m.append({"r":"user","c":q})
    with st.chat_message("user"): st.write(q)
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":q}]}, timeout=30).json()
        if "choices" not in r:
            ans=f"Erreur Groq: {r}"
        else:
            ans=r["choices"][0]["message"]["content"]
    except Exception as e:
        ans=f"Erreur: {e}"
    st.session_state.m.append({"r":"assistant","c":ans})
    with st.chat_message("assistant"): st.write(ans)
