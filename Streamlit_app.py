import streamlit as st, requests, base64, json, os

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
div[data-testid="stChatMessages"] {
    max-width:720px; margin:0 auto;
    padding-bottom:90px!important; gap:4px!important;
}

/* TES COULEURS D'ORIGINE - JE NE CHANGE RIEN */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    justify-content:flex-end!important; align-self:flex-end!important;
    max-width:75%!important; margin-left:auto!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important; /* TA COULEUR BEIGE D'ORIGINE */
    border-radius:18px 18px 4px 18px!important;
    padding:10px 14px!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) p {color:#111!important;}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    align-self:flex-start!important; max-width:75%!important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stMarkdownContainer"]{
    background:transparent!important; /* TA COULEUR D'ORIGINE */
    padding:6px 0!important;
}
.stChatMessage p {font-size:15.5px!important; line-height:1.7!important; color:#111!important;}

div[data-testid="stChatInput"] {
    max-width:720px; margin:0 auto;
    background:#f5f5f5!important; /* TA COULEUR D'ORIGINE */
    border:1px solid #e5e5e5!important; border-radius:24px!important;
}
</style>
""", unsafe_allow_html=True)

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
FILE = "angel_memory.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {c: [] for c in CLASSES}
def save():
    with open(FILE,"w",encoding="utf-8") as f: json.dump(st.session_state.chats, f, ensure_ascii=False, indent=2)

if "chats" not in st.session_state: st.session_state.chats = load()
if "classe" not in st.session_state: st.session_state.classe = "Terminale"
KEY = st.secrets.get("GROQ_API_KEY","").strip()

def ask(q, classe, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}"},{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof de {classe}."},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=40).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur"

cl = st.session_state.classe
st.markdown(f"""
<div style='max-width:720px; margin:0 auto; padding:12px 4px;'>
