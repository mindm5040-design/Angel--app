import streamlit as st, requests, base64, os, re, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="wide")
KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

def fix(t):
    if not t: return ""
    return re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', t, flags=re.DOTALL)

def get_video():
    p = Path("brain.mp4")
    if p.exists():
        try:
            b64 = base64.b64encode(p.read_bytes()).decode()
            return '<div class="brain-wrap"><video autoplay loop muted playsinline><source src="data:video/mp4;base64,' + b64 + '" type="video/mp4"></video></div>'
        except: pass
    return '<div class="brain-wrap"><div style="font-size:50px;line-height:88px;text-align:center">🧠</div></div>'

MEM_FILE = Path("angel_memory.json")
CONV_FILE = Path("angel_conversations.json")

def load_json(p, default):
    if p.exists():
        try:
            j=json.loads(p.read_text(encoding="utf-8"))
            return j if j else default
        except: return default
    return default

def save_json(p, data):
    try: p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except: pass

if "memory" not in st.session_state:
    st.session_state.memory = load_json(MEM_FILE, {"prenom":"", "niveau":"Premiere"})
if "conversations" not in st.session_state:
    st.session_state.conversations = load_json(CONV_FILE, [])
if "current_id" not in st.session_state:
    st.session_state.current_id = str(uuid.uuid4())
    st.session_state.messages = []
if "messages" not in st.session_state: st.session_state.messages = []
if "classe" not in st.session_state:
    st.session_state.classe = st.session_state.memory.get("niveau","Premiere")
if "mode" not in st.session_state: st.session_state.mode = "chat"
if "lang" not in st.session_state: st.session_state.lang = "Anglais"
if "in_call" not in st.session_state: st.session_state.in_call = False
if "is_typing" not in st.session_state: st.session_state.is_typing = False
if "pending_img" not in st.session_state: st.session_state.pending_img = None

LANG = {"Anglais":"en-US", "Espagnol":"es-ES", "Allemand":"de-DE"}

def ask(q, img=None, vocal=False):
    # DETECTION AUTO PRENOM
    low=q.lower()
    if any(x in low for x in ["appelle","je suis","moi c'est","m'appelle","c est"]):
        m=re.search(r"(?:appelle|suis|c'est|c est)\s+([A-Za-zÀ-ÿ]{2,20})", q, re.I)
        if m:
            st.session_state.memory["prenom"]=m.group(1).capitalize()
            save_json(MEM_FILE, st.session_state.memory)

    mem = st.session_state.memory
    prenom = mem.get("prenom","")
    base = f"Tu es Angel prof {st.session_state.classe}. Élève {prenom if prenom else 'prénom inconnu, demande-le si besoin'}."
    if vocal:
        base = f"You teach {st.session_state.lang}. Student {prenom}. Short answer 2-3 sentences."

    url = "https://api.groq.com/openai/v1/chat/completions"
    h = {"Authorization": "Bearer " + KEY}
    try:
        if img:
            b64 = base64.b64encode(img).decode()
            pl = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist = [{"role":x["role"],"content":x["content"][:400]} for x in st.session_state.messages[-6:]]
            pl = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}]}
        r = requests.post(url, headers=h, json=pl, timeout=90).json()
        if "choices" not in r: return "Erreur API, réessaie"
        return fix(r["choices"][0]["message"]["content"])
    except Exception as e:
        return f"Erreur {e}"

def save_current():
    if len(st.session_state.messages)<2: return
    first = [m for m in st.session_state.messages if m["role"]=="user"]
    title = first[0]["content"][:35] + "..." if first else "Nouvelle conversation"
    conv = {"id":st.session_state.current_id, "title":title, "messages":st.session_state.messages, "date":datetime.now().isoformat(), "classe":st.session_state.classe}
    all_c = load_json(CONV_FILE, [])
    all_c = [c for c in all_c if c["id"]!=st.session_state.current_id]
    all_c.insert(0, conv)
    save_json(CONV_FILE, all_c[:100])
    st.session_state.conversations = all_c
    save_json(MEM_FILE, st.session_state.memory)

# DESIGN CHIC + ANIMATIONS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@700&display=swap');
.stApp{background:#FFFCF8!important} header,footer,#MainMenu{display:none}
[data-testid='stSidebar']{background:#FFFEFB!important;border-right:1px solid #F0E8DE}
* {font-family:'Inter',sans-serif}
.brain-wrap{width:86px;height:86px;margin:0 auto;border-radius:50%;overflow:hidden;border:1.5px solid #E8DCCF;background:white;box-shadow:0 8px 24px rgba(224,122,79,0.18);animation:pulse 2.6s infinite}
.brain-wrap video{width:100%;height:100%;object-fit:cover}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06);box-shadow:0 12px 32px rgba(224,122,79,0.28)}}
div[data-testid="stChatMessage"]{background:white;border:1px solid #F0E8DE;border-radius:18px;margin-bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,0.03);animation:msgIn.38s ease}
div[data-testid="stChatMessage"] p{font-size:15px!important;line-height:1.7!important}
@keyframes msgIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.typing{display:flex;gap:6px;align-items:center;background:white;border:1px solid #F0E8DE;border-radius:20px;padding:10px 14px;width:fit-content;margin:8px 0}
.dot{width:6px;height:6px;background:#E07A4F;border-radius:50%;animation:b 1.3s infinite}
.dot:nth-child(2){animation-delay:.18s}.dot:nth-child(3){animation-delay:.36s}
@keyframes b{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:12px 0'>" + get_video() + "<div style='font-family:Space Grotesk;font-weight:700;font-size:18px'>Angel AI</div><div style='color:#E07A4F;font-size:10px;font-weight:700;letter-spacing:2px'>NEURAL ENGINE</div></div>", unsafe_allow_html=True)

    if st.button("✦ Nouvelle conversation", use_container_width=True, type="primary"):
        save_current()
        st.session_state.current_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    # PLUS DE CASE PRENOM - INFO
    if st.session_state.memory.get("prenom"):
        st.success(f"👤 {st.session_state.memory.get('prenom')} • {st.session_state.classe}")
    else:
        st.info("👋 Tape ton prénom dans le chat: *Je m'appelle...*")

    st.markdown(f"<div style='font-size:10px;font-weight:700;letter-spacing:1.5px;color:#9A8E84;margin:14px 0 8px'>ANCIENNES • {len(st.session_state.conversations)}</div>", unsafe_allow_html=True)
    for conv in st.session_state.conversations[:10]:
        is_active = conv["id"] == st.session_state.current_id
        label = ("● " if is_active else "") + conv["title"][:30]
        if st.button(label, key="conv_" + conv["id"], use_container_width=True, type="primary" if is_active else "secondary"):
            save_current()
            st.session_state.current_id = conv["id"]
            st.session_state.messages = conv["messages"]
            st.rerun()

    st.markdown("---")
    m = st.radio("", ["💬 Chat Études", "📞 Appel Gratuit"], label_visibility="collapsed")
    st.session_state.mode = "vocal" if "Appel" in m else "chat"
    if st.session_state.mode == "vocal":
        st.session_state.lang = st.selectbox("Langue", list(LANG.keys()))

    st.markdown("<div style='font-size:10px;font-weight:700;letter-spacing:1.5px;color:#9A8E84;margin:14px 0 8px'>NIVEAU</div>", unsafe_allow_html=True)
    cols=st.columns(2)
    for i,c in enumerate(["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]):
        with cols[i%2]:
            if st.button(c, key="cl_" + c, use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                st.session_state.classe = c
                st.session_state.memory["niveau"] = c
                save_json(MEM_FILE, st.session_state.memory)
                st.rerun()

    with st.expander("📸 Photo devoir"):
        up = st.file_uploader("Photo", type=["jpg","png","jpeg"], label_visibility="collapsed")
        cam = st.camera_input("Camera", label_visibility="collapsed")
        img = cam.getvalue() if cam else (up.getvalue() if up else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            st.session_state.pending_img = img
            st.session_state.messages.append({"role":"user","content":"📸 Photo"})
            st.session_state.is_typing = True
            st.rerun()

# HEADER CENTRAL
st.markdown("<div style='text-align:center'>" + get_video() + f"<div style='font-family:Space Grotesk;font-weight:700;font-size:26px'>Angel AI</div><div style='color:#E07A4F;font-size:10px;font-weight:700;letter-spacing:2px'>ACTIVE • {st.session_state.classe} • {len(st.session_state.conversations)} CONVS</div></div>", unsafe_allow_html=True)

if st.session_state.mode == "chat":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant":
                safe=m["content"][:300].replace("'"," ").replace('"'," ").replace("\n"," ")
                components.html(f"""
                    <button onclick="speechSynthesis.cancel();var u=new SpeechSynthesisUtterance('{safe}');u.lang='fr-FR';u.rate=0.95;speechSynthesis.speak(u);"
                    style="background:#111;color:white;border:none;border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer">🔊 Lire</button>
                    <button onclick="speechSynthesis.cancel()" style="background:white;border:1px solid #E8E3DC;border-radius:20px;padding:6px 10px;font-size:12px;margin-left:6px;cursor:pointer">⏹️</button>
                """, height=38)

    if st.session_state.is_typing:
        st.markdown('<div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div><span style="font-size:12px;color:#9A8E84;margin-left:6px">Angel écrit...</span></div>', unsafe_allow_html=True)
        q_last = [x for x in st.session_state.messages if x["role"]=="user"][-1]["content"] if st.session_state.messages else ""
        rep = ask(q_last, img=st.session_state.pending_img)
        st.session_state.messages.append({"role":"assistant","content":rep})
        st.session_state.is_typing=False
        st.session_state.pending_img=None
        save_current()
        safe_rep=rep[:280].replace("'"," ").replace('"'," ").replace("\n"," ")
        components.html(f"<script>try{{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance('{safe_rep}');u.lang='fr-FR';speechSynthesis.speak(u);}}catch(e){{}}</script>", height=0)
        time.sleep(0.4)
        st.rerun()

    q = st.chat_input(f"Question {st.session_state.classe}... (🎤 clavier pour parler)")
    if q:
        st.session_state.messages.append({"role":"user","content":q})
        st.session_state.is_typing=True
        st.rerun()
else:
    code = LANG[st.session_state.lang]
    if not st.session_state.in_call:
        st.markdown(f'<div style="background:white;border:1.5px solid #111;border-radius:20px;padding:24px;text-align:center"><div style="font-size:48px">📞</div><h3>Appel Gratuit - {st.session_state.lang}</h3><p>Gratuit comme WhatsApp</p></div>', unsafe_allow_html=True)
        if st.button("📞 LANCER L'APPEL", type="primary", use_container_width=True):
            st.session_state.in_call = True
            st.rerun()
    else:
        st.markdown(f'<div style="background:#111;color:white;border-radius:14px;padding:10px;text-align:center">En appel • {st.session_state.lang} • <span style="color:#25D366">En direct</span></div>', unsafe_allow_html=True)
        if st.button("🔴 Raccrocher", use_container_width=True):
            st.session_state.in_call = False
            st.rerun()
        for m in st.session_state.messages[-4:]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        qv = st.chat_input(f"Parle en {st.session_state.lang}... 🎤")
        if qv:
            st.session_state.messages.append({"role":"user","content":qv})
            rep = ask(qv, vocal=True)
            st.session_state.messages.append({"role":"assistant","content":rep})
            save_current()
            safe_rep=rep[:280].replace("'"," ").replace('"'," ")
            components.html(f"<script>try{{var u=new SpeechSynthesisUtterance('{safe_rep}');u.lang='{code}';speechSynthesis.speak(u);}}catch(e){{}}</script>", height=0)
            st.rerun()
