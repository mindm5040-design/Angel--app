import streamlit as st
st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")
import requests, base64, os, json, uuid, time, re
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY: st.stop()

MEM_FILE=Path("angel_memory.json")
CONV_FILE=Path("angel_conversations.json")
def load_json(p,d):
    if p.exists():
        try:
            j=json.loads(p.read_text(encoding="utf-8"))
            return j if j else d
        except: pass
    return d
def save_json(p,d):
    try: p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    except: pass

if "memory" not in st.session_state:
    st.session_state.memory=load_json(MEM_FILE,{"prenom":"","niveau":"Premiere"})
if "conversations" not in st.session_state:
    st.session_state.conversations=load_json(CONV_FILE,[])
if "current_id" not in st.session_state:
    st.session_state.current_id=str(uuid.uuid4())
    st.session_state.messages=[]
if "messages" not in st.session_state: st.session_state.messages=[]
if "classe" not in st.session_state: st.session_state.classe=st.session_state.memory.get("niveau","Premiere")
if "lang" not in st.session_state: st.session_state.lang="Anglais"
if "is_typing" not in st.session_state: st.session_state.is_typing=False
if "pending_img" not in st.session_state: st.session_state.pending_img=None

def get_brain():
    p=Path("brain.mp4")
    if p.exists():
        try:
            b64=base64.b64encode(p.read_bytes()).decode()
            return f'<div class="brain"><video autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video></div>'
        except: pass
    return '<div class="brain"><div style="font-size:62px;line-height:86px;text-align:center">🧠</div></div>'

LANG={"Anglais":"en-US","Espagnol":"es-ES","Allemand":"de-DE"}

def ask(q, img=None, vocal=False):
    low=q.lower()
    if any(x in low for x in ["appelle","je suis","moi c'est","m'appelle","c est"]):
        m=re.search(r"(?:appelle|suis|c'est|c est)\s+([A-Za-zÀ-ÿ]{2,20})", q, re.I)
        if m:
            st.session_state.memory["prenom"]=m.group(1).capitalize()
            save_json(MEM_FILE,st.session_state.memory)
    url="https://api.groq.com/openai/v1/chat/completions"
    h={"Authorization":"Bearer "+KEY}
    prenom=st.session_state.memory.get("prenom","")
    if vocal:
        base=f"You are Angel, friendly language tutor for {st.session_state.lang}. Student {prenom}, level {st.session_state.classe}. Keep answer 2-3 sentences, conversational, correct gently."
    else:
        base=f"Tu es Angel, prof {st.session_state.classe}. Élève {prenom if prenom else 'dont tu ne connais pas encore le prénom'}. Réponds clair, aéré, pédagogique. Maths avec $ $. Si tu ne connais pas le prénom, demande-le."

    try:
        if img:
            b64=base64.b64encode(img).decode()
            pl={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+"\nQuestion: "+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist=[{"role":x["role"],"content":x["content"][:500]} for x in st.session_state.messages[-6:]]
            pl={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}]}
        r=requests.post(url,headers=h,json=pl,timeout=90).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur réseau, réessaie."

def save_current():
    if len(st.session_state.messages)<2: return
    first=[m for m in st.session_state.messages if m["role"]=="user"]
    title=(first[0]["content"][:36]+"...") if first else "Nouvelle"
    conv={"id":st.session_state.current_id,"title":title,"messages":st.session_state.messages,"date":datetime.now().isoformat()}
    all_c=load_json(CONV_FILE,[])
    all_c=[c for c in all_c if c["id"]!=st.session_state.current_id]
    all_c.insert(0,conv)
    save_json(CONV_FILE,all_c[:100])
    st.session_state.conversations=all_c
    save_json(MEM_FILE,st.session_state.memory)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@700&display=swap');
.stApp{background:#FFFCF8!important} header,footer{display:none} *{font-family:'Inter',sans-serif}
.brain{width:88px;height:88px;margin:0 auto;border-radius:50%;overflow:hidden;border:1.5px solid #E8DCCF;background:white;box-shadow:0 8px 28px rgba(224,122,79,0.18);animation:pulse 2.6s infinite}
.brain video{width:100%;height:100%;object-fit:cover}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06);box-shadow:0 14px 36px rgba(224,122,79,0.30)}}
.title{font-family:'Space Grotesk'!important;font-size:28px!important;font-weight:700!important;text-align:center;margin-top:12px;color:#111}
.sub{color:#E07A4F;text-align:center;font-size:10px;font-weight:700;letter-spacing:2.2px;margin:4px 0 20px}
.card{background:white;border:1px solid #F0E8DE;border-radius:18px;padding:16px;margin-bottom:14px;box-shadow:0 2px 14px rgba(0,0,0,0.03)}
.label{font-size:10px;font-weight:700;letter-spacing:1.6px;color:#9A8E84;text-transform:uppercase;margin-bottom:12px}
div[data-testid="stButton"]>button{border-radius:12px!important;font-size:14px!important}
div[data-testid="stButton"]>button[kind="primary"]{background:#111!important;color:white!important;border:1px solid #111!important}
div[data-testid="stButton"]>button[kind="secondary"]{background:#FFFEFC!important;color:#111!important;border:1px solid #F0E8DE!important}
div[data-testid="stChatMessage"]{background:white;border:1px solid #F0E8DE;border-radius:18px;margin-bottom:10px;animation:in .38s ease}
div[data-testid="stChatMessage"] p{font-size:15.2px!important;line-height:1.7!important}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.typing{display:flex;gap:6px;align-items:center;background:white;border:1px solid #F0E8DE;border-radius:20px;padding:12px 16px;width:fit-content}
.dot{width:6px;height:6px;background:#E07A4F;border-radius:50%;animation:b 1.3s infinite}
.dot:nth-child(2){animation-delay:.18s}.dot:nth-child(3){animation-delay:.36s}
@keyframes b{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"{get_brain()}<div class='title'>Angel AI</div><div class='sub'>NEURAL ENGINE • {st.session_state.classe.upper()} • ACTIVE</div>", unsafe_allow_html=True)

if st.button("✦ Nouvelle conversation", use_container_width=True, type="primary"):
    save_current()
    st.session_state.current_id=str(uuid.uuid4())
    st.session_state.messages=[]
    st.rerun()

if not st.session_state.memory.get("prenom"):
    st.info("👋 Bienvenue ! Dis ton prénom dans le chat : *Je m'appelle ...*")
else:
    st.caption(f"👤 Connecté : {st.session_state.memory.get('prenom')} • {st.session_state.classe}")

st.markdown(f'<div class="card"><div class="label">Anciennes conversations • {len(st.session_state.conversations)} sauvegardées</div>', unsafe_allow_html=True)
for conv in st.session_state.conversations[:8]:
    if st.button(conv["title"][:42], key="c_"+conv["id"], use_container_width=True, type="secondary"):
        save_current()
        st.session_state.current_id=conv["id"]
        st.session_state.messages=conv["messages"]
        st.rerun()
if not st.session_state.conversations: st.caption("Aucune pour l'instant")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card"><div class="label">Niveau scolaire</div>', unsafe_allow_html=True)
cols=st.columns(2)
levels=["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]
for i,c in enumerate(levels):
    with cols[i%2]:
        if st.button(c, key="lv_"+c, use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
            st.session_state.classe=c
            st.session_state.memory["niveau"]=c
            save_json(MEM_FILE,st.session_state.memory)
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

mode=st.radio("", ["💬 Chat Études","📞 Appel Langues"], horizontal=True, label_visibility="collapsed")
is_vocal="Appel" in mode
if is_vocal:
    st.session_state.lang=st.selectbox("Langue", ["Anglais","Espagnol","Allemand"], label_visibility="collapsed")

with st.expander("📸 Photo de ton devoir"):
    up=st.file_uploader("Upload", type=["jpg","png","jpeg"], label_visibility="collapsed")
    cam=st.camera_input("Cam", label_visibility="collapsed")
    img=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser la photo", type="primary", use_container_width=True):
        st.session_state.pending_img=img
        st.session_state.messages.append({"role":"user","content":"📸 Photo de mon devoir"})
        st.session_state.is_typing=True
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"]=="assistant":
            safe=m["content"][:320].replace("'"," ").replace('"'," ").replace("\n"," ").replace("$","")
            lc=LANG[st.session_state.lang] if is_vocal else "fr-FR"
            components.html(f"""
                <button onclick="speechSynthesis.cancel();var u=new SpeechSynthesisUtterance('{safe}');u.lang='{lc}';u.rate=0.95;speechSynthesis.speak(u);" 
                style="background:#F5F0E8;border:1px solid #E8DCCF;border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer">🔊 Lire</button>
                <button onclick="speechSynthesis.cancel()" style="background:white;border:1px solid #E8E3DC;border-radius:20px;padding:6px 10px;font-size:12px;margin-left:6px;cursor:pointer">⏹️ Stop</button>
            """, height=40)

if st.session_state.is_typing:
    st.markdown('<div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div><span style="font-size:12px;color:#9A8E84;margin-left:6px">Angel écrit...</span></div>', unsafe_allow_html=True)
    q_last=[m for m in st.session_state.messages if m["role"]=="user"][-1]["content"] if st.session_state.messages else ""
    rep=ask(q_last, img=st.session_state.pending_img, vocal=is_vocal)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.session_state.is_typing=False
    st.session_state.pending_img=None
    save_current()
    safe_rep=rep[:280].replace("'"," ").replace('"'," ").replace("\n"," ")
    lc=LANG[st.session_state.lang] if is_vocal else "fr-FR"
    components.html(f"<script>try{{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance('{safe_rep}');u.lang='{lc}';speechSynthesis.speak(u);}}catch(e){{}}</script>", height=0)
    time.sleep(0.5)
    st.rerun()

q=st.chat_input("Tape ici... (micro 🎤 du clavier pour parler)")
if q:
    st.session_state.messages.append({"role":"user","content":q})
    st.session_state.is_typing=True
    st.rerun()
