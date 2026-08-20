import streamlit as st
import requests, base64, os, re, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="wide")
KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

def fix(t):
    if not t:
        return ""
    return re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', t, flags=re.DOTALL)

def get_video():
    p = Path("brain.mp4")
    if p.exists():
        try:
            b64 = base64.b64encode(p.read_bytes()).decode()
            return '<video style="width:100px;height:100px;border-radius:50%;border:2px solid #E07A4F" autoplay loop muted playsinline><source src="data:video/mp4;base64,' + b64 + '" type="video/mp4"></video>'
        except:
            pass
    return '<div style="font-size:50px">🧠</div>'

MEM_FILE = Path("angel_memory.json")
CONV_FILE = Path("angel_conversations.json")

def load_json(p, default):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except:
            return default
    return default

def save_json(p, data):
    try:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except:
        pass

if "memory" not in st.session_state:
    st.session_state.memory = load_json(MEM_FILE, {"prenom":"", "niveau":"Premiere"})
if "conversations" not in st.session_state:
    st.session_state.conversations = load_json(CONV_FILE, [])
if "current_id" not in st.session_state:
    st.session_state.current_id = str(uuid.uuid4())
    st.session_state.messages = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "classe" not in st.session_state:
    st.session_state.classe = st.session_state.memory.get("niveau","Premiere")
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "lang" not in st.session_state:
    st.session_state.lang = "Anglais"
if "in_call" not in st.session_state:
    st.session_state.in_call = False

LANG = {"Anglais":"en-US", "Espagnol":"es-ES", "Allemand":"de-DE"}

def ask(q, img=None, vocal=False):
    mem = st.session_state.memory
    # Si prenom vide, on le detecte auto dans le chat
    low = q.lower()
    if not mem.get("prenom") and any(x in low for x in ["appelle","je suis","moi c'est","m'appelle"]):
        m = re.search(r"(?:appelle|suis|c'est)\s+([A-Za-zÀ-ÿ]{2,20})", q, re.I)
        if m:
            mem["prenom"] = m.group(1).capitalize()
            save_json(MEM_FILE, mem)

    base = "Tu es Angel prof %s. Prenom %s. Reponse claire, lisible." % (st.session_state.classe, mem.get("prenom","élève"))
    if vocal:
        base = "You teach %s. %s Short answer 2-3 sentences." % (st.session_state.lang, base)
    url = "https://api.groq.com/openai/v1/chat/completions"
    h = {"Authorization": "Bearer " + KEY, "Content-Type":"application/json"}
    try:
        if img:
            b64 = base64.b64encode(img).decode()
            pl = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}], "max_tokens":1000}
        else:
            hist = [{"role":x["role"],"content":x["content"][:400]} for x in st.session_state.messages[-6:]]
            pl = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}], "max_tokens":1000}
        r = requests.post(url, headers=h, json=pl, timeout=90)
        data = r.json()
        if "choices" not in data:
            return f"Erreur API Groq: {data.get('error',{}).get('message', str(data)[:300])}"
        return fix(data["choices"][0]["message"]["content"])
    except Exception as e:
        return "Erreur reseau: %s" % e

def save_current():
    if not st.session_state.messages:
        return
    first = [m for m in st.session_state.messages if m["role"]=="user"]
    title = first[0]["content"][:35] + "..." if first else "Nouvelle conversation"
    conv = {"id":st.session_state.current_id, "title":title, "messages":st.session_state.messages, "date":datetime.now().strftime("%d/%m %H:%M"), "classe":st.session_state.classe}
    st.session_state.conversations = [c for c in st.session_state.conversations if c["id"]!=st.session_state.current_id]
    st.session_state.conversations.insert(0, conv)
    save_json(CONV_FILE, st.session_state.conversations[:50])
    save_json(MEM_FILE, st.session_state.memory)

st.markdown("<style>.stApp{background:#FCFCF9!important}header,footer,#MainMenu{display:none}[data-testid='stSidebar']{background:#F5F3EF!important}.brain-wrap{width:100px;height:100px;margin:0 auto;border-radius:50%;overflow:hidden;border:2px solid #E07A4F;animation:pulse 2.5s infinite}.brain-wrap video{width:100%;height:100%;object-fit:cover}@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:10px 0'>" + get_video() + "<div style='font-weight:700'>Angel AI</div><div style='color:#E07A4F;font-size:10px;font-weight:700'>NEURAL ENGINE</div></div>", unsafe_allow_html=True)
    if st.button("✦ Nouvelle conversation", use_container_width=True, type="primary"):
        save_current()
        st.session_state.current_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.markdown("ANCIENNES CONVERSATIONS")
    for conv in st.session_state.conversations[:12]:
        is_active = conv["id"] == st.session_state.current_id
        label = ("● " if is_active else "") + conv["title"][:28]
        if st.button(label, key="conv_" + conv["id"], use_container_width=True, type="primary" if is_active else "secondary"):
            save_current()
            st.session_state.current_id = conv["id"]
            st.session_state.messages = conv["messages"]
            st.rerun()
    st.markdown("---")
    st.session_state.memory["prenom"] = st.text_input("Prenom (ou tape 'je m'appelle...' dans le chat)", value=st.session_state.memory.get("prenom",""))
    m = st.radio("", ["💬 Chat", "📞 Appel Gratuit"], label_visibility="collapsed")
    st.session_state.mode = "vocal" if "Appel" in m else "chat"
    if st.session_state.mode == "vocal":
        st.session_state.lang = st.selectbox("Langue", list(LANG.keys()))
    st.markdown("Niveau")
    for c in ["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]:
        if st.button(c, key="cl_" + c, use_container_width=True, type="primary" if c==st
