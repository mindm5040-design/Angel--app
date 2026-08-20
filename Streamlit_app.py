import streamlit as st
st.set_page_config(page_title="Angel AI", layout="wide", initial_sidebar_state="collapsed")
import requests, base64, os, re, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY:
    st.error("Ajoute GROQ_API_KEY")
    st.stop()

components.html("<script>const pDoc=window.parent.document,pWin=window.parent;if(!pWin.angelCtx){pWin.angelCtx=new (window.AudioContext||window.webkitAudioContext)();pWin.speak=function(id){try{pWin.speechSynthesis.cancel();let el=pDoc.getElementById(id);let u=new SpeechSynthesisUtterance(el.innerText.substring(0,500));u.lang='fr-FR';pWin.speechSynthesis.speak(u);}catch(e){}};}</script>", height=0)

def get_video():
    p=Path("brain.mp4")
    if p.exists():
        b64=base64.b64encode(p.read_bytes()).decode()
        return '<video style="width:80px;height:80px;border-radius:50%" autoplay loop muted playsinline><source src="data:video/mp4;base64,'+b64+'" type="video/mp4"></video>'
    return '<div style="font-size:50px">🧠</div>'

MEM_FILE=Path("angel_memory.json")
CONV_FILE=Path("angel_conversations.json")

def load_json(p,d):
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return d
def save_json(p,data):
    try: p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    except: pass

if "memory" not in st.session_state:
    st.session_state.memory=load_json(MEM_FILE,{"prenom":"","niveau":"Premiere"})
if "conversations" not in st.session_state:
    st.session_state.conversations=load_json(CONV_FILE,[])
if "current_id" not in st.session_state:
    st.session_state.current_id=str(uuid.uuid4())
    st.session_state.messages=[]
if "messages" not in st.session_state:
    st.session_state.messages=[]
if "classe" not in st.session_state:
    st.session_state.classe="Premiere"
if "mode" not in st.session_state:
    st.session_state.mode="chat"

def ask(q,img=None):
    url="https://api.groq.com/openai/v1/chat/completions"
    h={"Authorization":"Bearer "+KEY}
    base="Tu es Angel prof "+st.session_state.classe+". Prenom "+st.session_state.memory.get("prenom","")+"."
    try:
        if img:
            b64=base64.b64encode(img).decode()
            pl={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist=[{"role":x["role"],"content":x["content"][:300]} for x in st.session_state.messages[-4:]]
            pl={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}]}
        r=requests.post(url,headers=h,json=pl,timeout=60).json()
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        return "Erreur %s" % e

def save_current():
    if not st.session_state.messages: return
    first=[m for m in st.session_state.messages if m["role"]=="user"]
    title=first[0]["content"][:35]+"..." if first else "Nouvelle conv"
    conv={"id":st.session_state.current_id,"title":title,"messages":st.session_state.messages,"date":datetime.now().strftime("%d/%m %H:%M")}
    st.session_state.conversations=[c for c in st.session_state.conversations if c["id"]!=st.session_state.current_id]
    st.session_state.conversations.insert(0,conv)
    save_json(CONV_FILE,st.session_state.conversations[:50])
    save_json(MEM_FILE,st.session_state.memory)

# HEADER VISIBLE SANS MENU
st.markdown("<div style='text-align:center'>"+get_video()+"<h2>Angel AI</h2><div style='color:#E07A4F;font-size:11px'>ACTIVE • "+st.session_state.classe+" • "+str(len(st.session_state.conversations))+" CONVS</div></div>", unsafe_allow_html=True)

# TOUTES LES DEMANDES VISIBLES ICI
c1,c2=st.columns(2)
with c1:
    if st.button("✦ Nouvelle conversation", use_container_width=True, type="primary"):
        save_current()
        st.session_state.current_id=str(uuid.uuid4())
        st.session_state.messages=[]
        st.rerun()
with c2:
    st.session_state.memory["prenom"]=st.text_input("Prenom", value=st.session_state.memory.get("prenom",""), label_visibility="collapsed", placeholder="Ton prenom")

# ANCIENNES CONVERSATIONS VISIBLES
if st.session_state.conversations:
    st.markdown("**Anciennes conversations:**")
    cols=st.columns(3)
    for i,conv in enumerate(st.session_state.conversations[:6]):
        with cols[i%3]:
            if st.button(conv["title"][:20], key="conv_"+conv["id"], use_container_width=True):
                save_current()
                st.session_state.current_id=conv["id"]
                st.session_state.messages=conv["messages"]
                st.rerun()

# NIVEAUX VISIBLES
st.markdown("**Niveau:**")
cols=st.columns(5)
levels=["6e","5e","4e","3e","Seconde","Premiere","Terminale","Licence 1","Master 1","Doctorat"]
for i,c in enumerate(levels):
    with cols[i%5]:
        if st.button(c, key="cl_"+c, use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
            st.session_state.classe=c
            st.session_state.memory["niveau"]=c
            save_json(MEM_FILE,st.session_state.memory)
            st.rerun()

# MODE
mode=st.radio("",["💬 Chat","📞 Appel Gratuit"], horizontal=True, label_visibility="collapsed")
st.session_state.mode="vocal" if "Appel" in mode else "chat"

# PHOTO VISIBLE
with st.expander("📸 Photo devoir - Clique ici"):
    up=st.file_uploader("Photo", type=["jpg","png"], label_visibility="collapsed")
    cam=st.camera_input("Camera", label_visibility="collapsed")
    img=cam.getvalue() if cam else (up.getvalue() if up else None)
    if img and st.button("Analyser le devoir", type="primary", use_container_width=True):
        rep=ask("Explique", img)
        st.session_state.messages.extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}])
        save_current()
        st.rerun()

st.markdown("---")

# CHAT
for i,m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown('<div id="msg-%s">%s</div>' % (i,m["content"]), unsafe_allow_html=True)
        if m["role"]=="assistant":
            components.html('<button onclick="window.parent.speak(\'msg-'+str(i)+'\')" style="background:#111;color:white;border:none;border-radius:20px;padding:5px 10px">🔊 Lire</button>', height=35)

q=st.chat_input("Question "+st.session_state.classe+"...")
if q:
    st.session_state.messages.append({"role":"user","content":q})
    rep=ask(q)
    st.session_state.messages.append({"role":"assistant","content":rep})
    save_current()
    st.rerun()
