import streamlit as st
st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")
import requests, base64, os, re, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY:
    st.error("Ajoute GROQ_API_KEY dans Secrets")
    st.stop()

# AUDIO FIX - marche sur tel
components.html("""
<script>
window.speakNow = function(t, lang){
  try{
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(t);
    u.lang = lang || 'fr-FR';
    u.rate = 0.95;
    u.volume = 1;
    var vs = window.speechSynthesis.getVoices();
    var f = vs.find(v => v.lang.includes(lang||'fr'));
    if(f) u.voice = f;
    window.speechSynthesis.speak(u);
  }catch(e){ console.log(e); }
};
window.speechSynthesis.getVoices();
window.speechSynthesis.onvoiceschanged = function(){ window.speechSynthesis.getVoices(); };
</script>
""", height=0)

def get_video():
    p = Path("brain.mp4")
    if p.exists():
        try:
            b64 = base64.b64encode(p.read_bytes()).decode()
            return '<video style="width:90px;height:90px;border-radius:50%;border:2px solid #E07A4F" autoplay loop muted playsinline><source src="data:video/mp4;base64,'+b64+'" type="video/mp4"></video>'
        except: pass
    return '<div style="font-size:50px;text-align:center">🧠</div>'

MEM_FILE = Path("angel_memory.json")
CONV_FILE = Path("angel_conversations.json")

def load_json(p,d):
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return d
def save_json(p,d):
    try: p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    except: pass

if "memory" not in st.session_state:
    st.session_state.memory = load_json(MEM_FILE, {"prenom":"","niveau":"Premiere"})
if "conversations" not in st.session_state:
    st.session_state.conversations = load_json(CONV_FILE, [])
if "current_id" not in st.session_state:
    st.session_state.current_id = str(uuid.uuid4())
    st.session_state.messages = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "classe" not in st.session_state:
    st.session_state.classe = st.session_state.memory.get("niveau","Premiere")
if "lang" not in st.session_state:
    st.session_state.lang = "Anglais"

LANG = {"Anglais":"en-US","Espagnol":"es-ES","Allemand":"de-DE"}

def ask(q, img=None, vocal=False):
    url = "https://api.groq.com/openai/v1/chat/completions"
    h = {"Authorization":"Bearer "+KEY}
    base = "Tu es Angel prof %s. Prenom %s. Reponds court avec maths $ $." % (st.session_state.classe, st.session_state.memory.get("prenom",""))
    if vocal:
        base = "You teach %s. %s 2 sentences max." % (st.session_state.lang, base)
    try:
        if img:
            b64 = base64.b64encode(img).decode()
            pl = {"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist = [{"role":x["role"],"content":x["content"][:300]} for x in st.session_state.messages[-4:]]
            pl = {"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}]}
        r = requests.post(url, headers=h, json=pl, timeout=60).json()
        if "choices" not in r:
            return "Erreur API"
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return "Erreur %s" % e

def save_current():
    if not st.session_state.messages: return
    first = [m for m in st.session_state.messages if m["role"]=="user"]
    title = first[0]["content"][:35]+"..." if first else "Nouvelle conversation"
    conv = {"id":st.session_state.current_id,"title":title,"messages":st.session_state.messages,"date":datetime.now().strftime("%d/%m %H:%M")}
    st.session_state.conversations = [c for c in st.session_state.conversations if c["id"]!=st.session_state.current_id]
    st.session_state.conversations.insert(0, conv)
    save_json(CONV_FILE, st.session_state.conversations[:50])
    save_json(MEM_FILE, st.session_state.memory)

# HEADER
st.markdown("<div style='text-align:center;padding:10px 0'>"+get_video()+"<div style='font-weight:700;font-size:20px'>Angel AI</div><div style='color:#E07A4F;font-size:10px;font-weight:700'>NEURAL ENGINE • ACTIVE</div></div>", unsafe_allow_html=True)

c1,c2 = st.columns([2,1])
with c1:
    if st.button("✦ Nouvelle conversation", use_container_width=True, type="primary"):
        save_current()
        st.session_state.current_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
with c2:
    st.session_state.memory["prenom"] = st.text_input("Prenom", value=st.session_state.memory.get("prenom",""), placeholder="Prenom", label_visibility="collapsed")

if st.session_state.conversations:
    st.markdown("**Anciennes conversations:**")
    cols = st.columns(3)
    for i,conv in enumerate(st.session_state.conversations[:6]):
        with cols[i%3]:
            if st.button(conv["title"][:22], key="conv_"+conv["id"], use_container_width=True):
                save_current()
                st.session_state.current_id = conv["id"]
                st.session_state.messages = conv["messages"]
                st.rerun()

st.markdown("**Niveau:**")
cols = st.columns(5)
for i,c in enumerate(["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]):
    with cols[i%5]:
        if st.button(c, key="cl_"+c, use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
            st.session_state.classe = c
            st.session_state.memory["niveau"] = c
            save_json(MEM_FILE, st.session_state.memory)
            st.rerun()

mode = st.radio("", ["💬 Chat Etudes","📞 Appel Langues"], horizontal=True, label_visibility="collapsed")
is_vocal = "Appel" in mode
if is_vocal:
    st.session_state.lang = st.selectbox("Langue d'appel", list(LANG.keys()), label_visibility="collapsed")

with st.expander("📸 Photo devoir"):
    up = st.file_uploader("Photo", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam = st.camera_input("Camera", label_visibility="collapsed")
    img = cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser", type="primary", use_container_width=True):
        rep = ask("Explique cet exercice etape par etape", img)
        st.session_state.messages.extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}])
        save_current()
        st.rerun()

st.markdown("---")

# AFFICHAGE CHAT AVEC AUDIO
for i,m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"]=="assistant":
            safe = m["content"][:350].replace("'"," ").replace('"'," ").replace("\n"," ").replace("`"," ")
            lang_code = LANG[st.session_state.lang] if is_vocal else "fr-FR"
            components.html("""
                <button onclick="speakNow('TEXT','LANG')" style="background:#111;color:white;border:none;border-radius:20px;padding:8px 14px;cursor:pointer">🔊 Lire</button>
                <button onclick="window.speechSynthesis.cancel()" style="background:#eee;border:none;border-radius:20px;padding:8px 10px;margin-left:6px;cursor:pointer">⏹️ Stop</button>
            """.replace("TEXT", safe).replace("LANG", lang_code), height=45)

q = st.chat_input("Parle ici... (micro du clavier pour parler)")
if q:
    st.session_state.messages.append({"role":"user","content":q})
    if is_vocal:
        rep = ask(q, vocal=True)
        lang_code = LANG[st.session_state.lang]
    else:
        rep = ask(q)
        lang_code = "fr-FR"
    st.session_state.messages.append({"role":"assistant","content":rep})
    save_current()
    # auto lecture
    safe_rep = rep[:350].replace("'"," ").replace('"'," ").replace("\n"," ").replace("`"," ")
    components.html("<script>speakNow('%s','%s')</script>" % (safe_rep, lang_code), height=0)
    st.rerun()
