import streamlit as st, requests, base64, os, re, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="wide")
KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

components.html("<script>const pDoc=window.parent.document,pWin=window.parent;if(!pWin.angelCtx){pWin.angelCtx=new (window.AudioContext||window.webkitAudioContext)();pWin.playDing=function(){try{let o=pWin.angelCtx.createOscillator(),g=pWin.angelCtx.createGain();o.frequency.value=1200;o.connect(g);g.connect(pWin.angelCtx.destination);g.gain.setValueAtTime(0.6,pWin.angelCtx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,pWin.angelCtx.currentTime+0.5);o.start();o.stop(pWin.angelCtx.currentTime+0.5);}catch(e){}};pWin.speak=function(id){try{pWin.speechSynthesis.cancel();let el=pDoc.getElementById(id);if(!el)return;let u=new SpeechSynthesisUtterance(el.innerText.substring(0,600));u.lang='fr-FR';pWin.speechSynthesis.speak(u);}catch(e){}};pWin.stopSpeak=function(){try{pWin.speechSynthesis.cancel();}catch(e){}};}</script>", height=0)

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
    base = "Tu es Angel prof %s. Prenom %s." % (st.session_state.classe, mem.get("prenom",""))
    if vocal:
        base = "You teach %s. %s Short answer." % (st.session_state.lang, base)
    url = "https://api.groq.com/openai/v1/chat/completions"
    h = {"Authorization": "Bearer " + KEY}
    try:
        if img:
            b64 = base64.b64encode(img).decode()
            pl = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist = [{"role":x["role"],"content":x["content"][:350]} for x in st.session_state.messages[-4:]]
            pl = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}]}
        r = requests.post(url, headers=h, json=pl, timeout=60).json()
        if "choices" not in r:
            return "Erreur API"
        return fix(r["choices"][0]["message"]["content"])
    except Exception as e:
        return "Erreur %s" % e

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

st.markdown("<style>.stApp{background:#FCFCF9!important}header,footer,#MainMenu{display:none}[data-testid='stSidebar']{background:#F5F3EF!important}</style>", unsafe_allow_html=True)

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
    st.session_state.memory["prenom"] = st.text_input("Prenom", value=st.session_state.memory.get("prenom",""))
    m = st.radio("", ["💬 Chat", "📞 Appel Gratuit"], label_visibility="collapsed")
    st.session_state.mode = "vocal" if "Appel" in m else "chat"
    if st.session_state.mode == "vocal":
        st.session_state.lang = st.selectbox("Langue", list(LANG.keys()))
    st.markdown("Niveau")
    for c in ["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]:
        if st.button(c, key="cl_" + c, use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
            st.session_state.classe = c
            st.session_state.memory["niveau"] = c
            save_json(MEM_FILE, st.session_state.memory)
            st.rerun()
    with st.expander("Photo devoir"):
        up = st.file_uploader("Photo", type=["jpg","png","jpeg"], label_visibility="collapsed")
        cam = st.camera_input("Camera", label_visibility="collapsed")
        img = cam.getvalue() if cam else (up.getvalue() if up else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            rep = ask("Explique", img)
            st.session_state.messages.extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}])
            save_current()
            st.rerun()

st.markdown("<div style='text-align:center'>" + get_video() + "<h2>Angel AI</h2><div style='color:#E07A4F;font-size:10px;font-weight:700'>ACTIVE • " + st.session_state.classe + " • " + str(len(st.session_state.conversations)) + " CONVS</div></div>", unsafe_allow_html=True)

if st.session_state.mode == "chat":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown('<div id="msg-%s">%s</div>' % (i, m["content"]), unsafe_allow_html=True)
            if m["role"] == "assistant":
                components.html('<script>try{window.parent.playDing();}catch(e){}</script>', height=0)
                components.html('<button onclick="window.parent.speak(\'msg-' + str(i) + '\')" style="background:#111;color:white;border:none;border-radius:20px;padding:6px 12px">🔊 Lire</button>', height=35)
    q = st.chat_input("Question " + st.session_state.classe + "...")
    if q:
        st.session_state.messages.append({"role":"user","content":q})
        rep = ask(q)
        st.session_state.messages.append({"role":"assistant","content":rep})
        save_current()
        st.rerun()
else:
    code = LANG[st.session_state.lang]
    if not st.session_state.in_call:
        st.markdown('<div style="background:white;border:2px solid #111;border-radius:20px;padding:20px;text-align:center"><div style="font-size:50px">📞</div><h3>Appel Gratuit - ' + st.session_state.lang + '</h3><p>Gratuit comme WhatsApp</p></div>', unsafe_allow_html=True)
        if st.button("📞 LANCER L APPEL", type="primary", use_container_width=True):
            st.session_state.in_call = True
            st.rerun()
    else:
        st.markdown('<div style="background:#111;color:white;border-radius:15px;padding:10px;text-align:center">En appel • ' + st.session_state.lang + ' • <span style="color:#25D366">En direct</span></div>', unsafe_allow_html=True)
        if st.button("🔴 Raccrocher", use_container_width=True):
            st.session_state.in_call = False
            st.rerun()
        st.markdown("Clique 🎤 dans la zone de texte en bas pour parler")
        for m in st.session_state.messages[-4:]:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        qv = st.chat_input("Parle en " + st.session_state.lang + "...")
        if qv:
            st.session_state.messages.append({"role":"user","content":qv})
            rep = ask(qv, vocal=True)
            st.session_state.messages.append({"role":"assistant","content":rep})
            save_current()
            st.rerun()
