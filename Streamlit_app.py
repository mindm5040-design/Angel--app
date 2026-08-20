import streamlit as st, requests, base64, json, os, uuid
from datetime import datetime

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap');

/* FOND COMME MOI */
.stApp {background:#fbfaf8!important;}
section[data-testid="stSidebar"] {background:#f2f0eb!important; border-right:1px solid #e8e0d6!important;}
div[data-testid="stSidebar"] * {font-family:'Inter', sans-serif!important;}

/* CHAT COMME MOI - CENTRÉ, LISBLE */
div[data-testid="stChatMessages"] {
    max-width:720px!important; margin:0 auto!important;
    gap:28px!important; padding-top:30px!important; padding-bottom:120px!important;
}
.stChatMessage {background:transparent!important; border:none!important; padding:0!important;}
.stChatMessage p,.stChatMessage li {
    font-family:'Source Serif 4', Georgia, serif!important;
    font-size:16px!important; line-height:1.85!important; color:#111!important;
    letter-spacing:-0.01em!important;
}
.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    display:flex; justify-content:flex-end!important;
}
.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"]{
    background:#efe9dd!important;
    border-radius:24px 24px 6px 24px!important;
    padding:14px 18px!important;
    max-width:75%!important;
    font-family:'Inter', sans-serif!important;
}
.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stMarkdownContainer"]{
    background:transparent!important; padding:0!important;
}

/* INPUT COMME MOI - PILULE AVEC + */
div[data-testid="stChatInput"] {
    max-width:720px!important; margin:0 auto!important;
    background:white!important; border:1px solid #e2ddd3!important;
    border-radius:28px!important; box-shadow:0 2px 16px rgba(0,0,0,0.06)!important;
    padding:6px 10px!important;
}
div[data-testid="stChatInput"] textarea {
    font-family:'Inter', sans-serif!important; font-size:16px!important;
}

/* BOUTONS SALLES */
.salle-active {background:#111!important; color:white!important; border-radius:10px!important;}
</style>
""", unsafe_allow_html=True)

CLASSES = ["6e","5e","4e","3e","Seconde","Première","Terminale","Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
FILE = "angel_design.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"convs":[], "active":None}

def save():
    with open(FILE,"w",encoding="utf-8") as f: json.dump(st.session_state.data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state: st.session_state.data = load()
if "classe" not in st.session_state: st.session_state.classe = "Terminale"

KEY = st.secrets.get("GROQ_API_KEY","").strip()

def ask(q, classe, img=None):
    if img:
        b64=base64.b64encode(img).decode()
        body={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}"},{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]}
    else:
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel, prof {classe}. Réponse claire, structurée, comme Claude. Programme strict {classe}."},{"role":"user","content":q}]}
    r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=40).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur"

def new_chat():
    c={"id":str(uuid.uuid4())[:6], "title":"Nouvelle conversation", "classe":st.session_state.classe, "msgs":[], "date":datetime.now().strftime("%d/%m")}
    st.session_state.data["convs"].insert(0,c); st.session_state.data["active"]=c["id"]; save()

def get_active():
    aid=st.session_state.data["active"]
    for x in st.session_state.data["convs"]:
        if x["id"]==aid: return x
    return None

# --- SIDEBAR DESIGN COMME CHATGPT ---
with st.sidebar:
    st.markdown("<div style='padding:10px 6px; font-weight:600; font-size:18px;'>🕊️ Angel</div>", unsafe_allow_html=True)

    if st.button("⊕ Nouveau chat", use_container_width=True):
        new_chat(); st.rerun()

    st.markdown("<div style='margin:20px 0 8px 6px; font-size:12px; letter-spacing:0.08em; color:#888; font-weight:600;'>SALLES DE CLASSE</div>", unsafe_allow_html=True)
    for cl in CLASSES:
        act = st.session_state.classe == cl
        if st.button(f"{'●' if act else '○'} {cl}", key=f"cl_{cl}", use_container_width=True, type="primary" if act else "secondary"):
            st.session_state.classe = cl; new_chat(); st.rerun()

    st.markdown("<div style='margin:20px 0 8px 6px; font-size:12px; letter-spacing:0.08em; color:#888; font-weight:600;'>OUTILS</div>", unsafe_allow_html=True)
    up = st.file_uploader("Photo", type=["jpg","png"], label_visibility="collapsed", key="up")
    cam = st.camera_input("Caméra", label_visibility="collapsed")
    aud = st.audio_input("Vocal", label_visibility="collapsed")

    st.markdown("<div style='margin:20px 0 8px 6px; font-size:12px; letter-spacing:0.08em; color:#888; font-weight:600;'>HISTORIQUE</div>", unsafe_allow_html=True)
    for conv in st.session_state.data["convs"][:15]:
        sel = conv["id"]==st.session_state.data["active"]
        if st.button(f"{conv['title'][:22]} • {conv['classe']}", key=f"h_{conv['id']}", use_container_width=True, type="primary" if sel else "secondary"):
            st.session_state.data["active"]=conv["id"]; st.session_state.classe=conv["classe"]; st.rerun()

# --- CHAT PRINCIPAL COMME MOI ---
ac = get_active()

if not ac:
    st.markdown(f"""
    <div style='max-width:720px; margin:80px auto; text-align:center;'>
        <div style='width:48px; height:48px; background:#111; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px; font-size:20px;'>🕊️</div>
        <h1 style='font-family:Inter; font-weight:600; letter-spacing:-0.02em; font-size:28px;'>Comment puis-je t'aider aujourd'hui, en {st.session_state.classe}?</h1>
        <p style='color:#777; font-family:Inter; margin-top:12px;'>Photo • Vocal • Mémoire • Salles 6e → Doctorat</p>
        <div style='margin-top:32px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;'>
            <span style='border:1px solid #e5e0d6; border-radius:20px; padding:8px 14px; font-size:13px;'>📸 Analyse d'exercice</span>
            <span style='border:1px solid #e5e0d6; border-radius:20px; padding:8px 14px; font-size:13px;'>🎙️ Explique à l'oral</span>
            <span style='border:1px solid #e5e0d6; border-radius:20px; padding:8px 14px; font-size:13px;'>📚 Programme {st.session_state.classe}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for m in ac["msgs"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# Actions
img = (cam.getvalue() if cam else None) or (up.getvalue() if up and hasattr(up,'getvalue') else None)
if img and ac and st.button(f"Analyser"):
    ans=ask("Corrige cet exercice", ac["classe"], img)
    ac["msgs"].extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":ans}]); save(); st.rerun()

if st.session_state.get("aud") and ac:
    try:
        files={"file":("a.wav", st.session_state.aud.getvalue(), "audio/wav")}; data={"model":"whisper-large-v3","language":"fr"}
        txt=requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {KEY}"}, files=files, data=data, timeout=60).json().get("text","")
        if txt:
            ac["msgs"].append({"role":"user","content":txt})
            ac["msgs"].append({"role":"assistant","content":ask(txt, ac["classe"])}); save(); st.rerun()
    except: pass

q = st.chat_input(f"Message à Angel • {st.session_state.classe}")
if q and ac:
    if len(ac["msgs"])==0: ac["title"]=q[:28]
    ac["msgs"].append({"role":"user","content":q})
    ac["msgs"].append({"role":"assistant","content":ask(q, ac["classe"])})
    save(); st.rerun()
elif q and not ac:
    new_chat(); ac=get_active()
    ac["title"]=q[:28]; ac["msgs"].append({"role":"user","content":q})
    ac["msgs"].append({"role":"assistant","content":ask(q, ac["classe"])})
    save(); st.rerun()
