import streamlit as st, requests, base64, os, re, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI - by Lelouch", page_icon="🧠", layout="wide")
KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
if not KEY: st.error("Ajoute GROQ_API_KEY dans Secrets"); st.stop()

components.html("""
<script>
const pDoc=window.parent.document, pWin=window.parent;
if(!pWin.angelCtx){
 pWin.angelCtx=new (pWin.AudioContext||pWin.webkitAudioContext)();
 pWin.playPop=()=>{try{let o=pWin.angelCtx.createOscillator(),g=pWin.angelCtx.createGain();o.frequency.value=800;o.connect(g);g.connect(pWin.angelCtx.destination);g.gain.setValueAtTime(0.8,pWin.angelCtx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,pWin.angelCtx.currentTime+0.2);o.start();o.stop(pWin.angelCtx.currentTime+0.2);}catch(e){}};
 pWin.playDing=()=>{try{let o=pWin.angelCtx.createOscillator(),g=pWin.angelCtx.createGain();o.frequency.value=1200;o.connect(g);g.connect(pWin.angelCtx.destination);g.gain.setValueAtTime(0.6,pWin.angelCtx.currentTime);g.gain.exponentialRampToValueAtTime(0.01,pWin.angelCtx.currentTime+0.5);o.start();o.stop(pWin.angelCtx.currentTime+0.5);}catch(e){}};
 pWin.playRing=()=>{try{let ctx=pWin.angelCtx,now=ctx.currentTime;[0,1,2].forEach(i=>{let o=ctx.createOscillator(),g=ctx.createGain();o.frequency.value=500;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(0.4,now+i);g.gain.linearRampToValueAtTime(0,now+i+0.7);o.start(now+i);o.stop(now+i+0.7);});}catch(e){}};
 pWin.speak=(id,lang)=>{try{pWin.speechSynthesis.cancel();let el=pDoc.getElementById(id);if(!el)return;let t=el.innerText.replace(/\\$\\$/g,' ').substring(0,600);let u=new SpeechSynthesisUtterance(t);u.lang=lang||'fr-FR';u.rate=0.95;pWin.speechSynthesis.speak(u);}catch(e){}};
 pWin.speakTxt=(t,l)=>{try{pWin.speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(t);u.lang=l||'fr-FR';u.rate=0.9;pWin.speechSynthesis.speak(u);}catch(e){}};
 pWin.stopSpeak=()=>{try{pWin.speechSynthesis.cancel();}catch(e){}};
 pDoc.addEventListener('click',e=>{if(e.target.closest('button[data-testid="stChatInputSubmitButton"]'))pWin.playPop();},true);
}
</script>
""", height=0)

def fix(t):
    if not t: return t
    return re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', t.replace("$$\\LaTeX$$",""), flags=re.DOTALL)

def get_video(s=110):
    for p in [Path("brain.mp4"), Path("angel-ai.mp4")]:
        if p.exists():
            try:
                b64=base64.b64encode(p.read_bytes()).decode()
                return f'<video style="width:{s}px;height:{s}px;border-radius:50%;object-fit:cover;border:2px solid #E07A4F;box-shadow:0 0 30px rgba(224,122,79,0.3)" autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
            except: pass
    return f'<div style="font-size:{s//2}px;text-align:center">🧠</div>'

MEM_FILE=Path("angel_memory.json")
CONV_FILE=Path("angel_conversations.json")

def load_json(p, default):
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return default

def save_json(p, data):
    try: p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except: pass

if "memory" not in st.session_state:
    st.session_state.memory=load_json(MEM_FILE, {"prenom":"","niveau":"Premiere","resume":"Nouveau","conv":0})
if "conversations" not in st.session_state:
    st.session_state.conversations=load_json(CONV_FILE, [])
if "current_id" not in st.session_state:
    st.session_state.current_id=str(uuid.uuid4())
    st.session_state.messages=[]
else:
    found=[c for c in st.session_state.conversations if c["id"]==st.session_state.current_id]
    if found and "messages" not in st.session_state:
        st.session_state.messages=found[0]["messages"]
if "messages" not in st.session_state:
    st.session_state.messages=[]

if "classe" not in st.session_state: st.session_state.classe=st.session_state.memory.get("niveau","Premiere")
if "mode" not in st.session_state: st.session_state.mode="chat"
if "lang" not in st.session_state: st.session_state.lang="Anglais"
if "in_call" not in st.session_state: st.session_state.in_call=False

LANG={"Anglais":"en-US","Espagnol":"es-ES","Allemand":"de-DE","Italien":"it-IT"}

def ask(q,img=None,vocal=False):
    mem=st.session_state.memory
    base=f"Mémoire: prenom={mem.get('prenom','')} niveau={mem.get('niveau','')} resume={mem.get('resume','')}. Tu es Angel prof {st.session_state.classe}. Maths $ $ $$ $$. Jamais mot LaTeX."
    if vocal: base=f"You are Angel on PHONE CALL teaching {st.session_state.lang}. {base} Short 2 sentences: correction FR then question in {st.session_state.lang}."
    url="https://api.groq.com/openai/v1/chat/completions"
    h={"Authorization":f"Bearer {KEY}"}
    try:
        if img:
            b64=base64.b64encode(img).decode()
            pl={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":[{"type":"text","text":base+q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}}]}]}
        else:
            hist=[{"role":x["role"],"content":x["content"][:350]} for x in st.session_state.messages[-4:]]
            pl={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":base}]+hist+[{"role":"user","content":q}]}
        r=requests.post(url,headers=h,json=pl,timeout=60).json()
        if "choices" not in r: return f"Erreur API: {r}"
        return fix(r["choices"][0]["message"]["content"])
    except Exception as e: return f"Erreur {e}"

def save_current_conv():
    if not st.session_state.messages: return
    first_user=[m for m in st.session_state.messages if m["role"]=="user"]
    title=first_user[0]["content"][:40]+"..." if first_user else "Nouvelle conversation"
    conv={"id":st.session_state.current_id,"title":title,"messages":st.session_state.messages,"date":datetime.now().strftime("%d/%m %H:%M"),"classe":st.session_state.classe}
    st.session_state.conversations=[c for c in st.session_state.conversations if c["id"]!=st.session_state.current_id]
    st.session_state.conversations.insert(0, conv)
    save_json(CONV_FILE, st.session_state.conversations[:50])
    save_json(MEM_FILE, st.session_state.memory)

st.markdown("""
<style>
.stApp{background:#FCFCF9!important}
header,footer,#MainMenu{display:none}
[data-testid="stSidebar"]{background:#F5F3EF!important; border-right:1px solid #E8E3DC!important}
.badge{color:#E07A4F;font-size:10px;letter-spacing:2.5px;font-weight:700}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='text-align:center;padding:16px 0'>{get_video(90)}<div style='font-family:Space Grotesk;font-weight:700;font-size:18px;margin-top:8px'>Angel AI</div><div class='badge'>NEURAL ENGINE • ACTIVE</div></div>", unsafe_allow_html=True)

    if st.button("✦ Nouvelle conversation", use_container_width=True, type="primary"):
        save_current_conv()
        st.session_state.current_id=str(uuid.uuid4())
        st.session_state.messages=[]
        st.rerun()

    st.markdown("<div style='margin:14px 0 6px;font-size:11px;letter-spacing:2px;color:#999;font-weight:700'>ANCIENNES CONVERSATIONS</div>", unsafe_allow_html=True)
    if not st.session_state.conversations:
        st.caption("Aucune conversation")
    else:
        for conv in st.session_state.conversations[:15]:
            is_active=conv["id"]==st.session_state.current_id
            label=f"{'● ' if is_active else ''}{conv['title'][:30]}"
            if st.button(label, key=f"conv_{conv['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
                save_current_conv()
                st.session_state.current_id=conv["id"]
                st.session_state.messages=conv["messages"]
                st.session_state.classe=conv.get("classe","Premiere")
                st.rerun()

    st.markdown("---")
    st.session_state.memory["prenom"]=st.text_input("👤 Prénom", value=st.session_state.memory.get("prenom",""))

    st.markdown("### Mode")
    mode=st.radio("",["💬 Chat Études","📞 Appel Gratuit Langues"], label_visibility="collapsed")
    st.session_state.mode="vocal" if "Appel" in mode else "chat"
    if st.session_state.mode=="vocal":
        st.session_state.lang=st.selectbox("Langue", list(LANG.keys()), label_visibility="collapsed")

    st.markdown("### 📚 Niveau")
    for label,items in [("COLLEGE",["6e","5e","4e","3e"]),("LYCEE",["Seconde","Premiere","Terminale"]),("UNIV",["Licence 1","Master 1","Doctorat"])]:
        st.caption(label)
        cols=st.columns(3)
        for i,c in enumerate(items):
            with cols[i%3]:
                if st.button(c, key=f"cl_{c}", use_container_width=True, type="primary" if c==st.session_state.classe else "secondary"):
                    st.session_state.classe=c; st.session_state.memory["niveau"]=c; save_json(MEM_FILE, st.session_state.memory); st.rerun()

    with st.expander("📸 Photo devoir"):
        up=st.file_uploader("Photo", type=["jpg","png","jpeg"], label_visibility="collapsed")
        cam=st.camera_input("Caméra", label_visibility="collapsed")
        img=cam.getvalue() if cam else (up.getvalue() if up else None)
        if img and st.button("Analyser", type="primary", use_container_width=True):
            rep=ask("Explique cet exercice étape par étape", img)
            st.session_state.messages.extend([{"role":"user","content":"📸 Photo"},{"role":"assistant","content":rep}])
            save_current_conv()
            st.rerun()

    if st.button("🗑️ Effacer tout", use_container_width=True):
        st.session_state.conversations=[]; save_json(CONV_FILE, []); st.session_state.messages=[]; st.rerun()

st.markdown(f"<div style='text-align:center;margin:8px 0'>{get_video(110)}<div style='font-family:Space Grotesk;font-size:36px;font-weight:700'>Angel AI</div><div class='badge'>ACTIVE • {st.session_state.memory.get('prenom','')} • {st.session_state.classe} • {len(st.session_state.conversations)} CONVS</div></div>", unsafe_allow_html=True)

if st.session_state.mode=="chat":
    if not st.session_state.messages:
        st.markdown(f"<div style='text-align:center;margin:30px 0;color:#999'><div style='font-size:44px'>✦</div><div style='font-size:18px;color:#111;margin-top:8px'>Bonjour {st.session_state.memory.get('prenom','Lelouch')}!</div><div style='font-size:13px;margin-top:4px'>Nouvelle conversation prête</div></div>", unsafe_allow_html=True)

    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(f'<div id="msg-{i}">{fix(m["content"])}</div>', unsafe_allow_html=True)
            if m["role"]=="assistant":
                components.html("<script>try{window.parent.playDing();}catch(e){}</script>", height=0)
                components.html(f"""<button onclick="window.parent.speak('msg-{i}','fr-FR')" style="background:#111;color:white;border:none;border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer">🔊 Lire</button><button onclick="window.parent.stopSpeak()" style="background:#eee;border:none;border-radius:20px;padding:6px 10px;margin-left:6px;cursor:pointer">⏹️</button>""", height=40)

    q=st.chat_input(f"Question {st.session_state.classe}...")
    if q:
        st.session_state.messages.append({"role":"user","content":q})
        st.session_state.memory["conv"]=st.session_state.memory.get("conv",0)+1
        rep=ask(q)
        st.session_state.messages.append({"role":"assistant","content":rep})
        save_current_conv()
        st.rerun()

else:
    code=LANG[st.session_state.lang]
    if not st.session_state.in_call:
        st.markdown(f"<div style='background:white;border:2px solid #111;border-radius:24px;padding:28px;text-align:center'><div style='font-size:56px'>📞</div><h2>Appel Gratuit - {st.session_state.lang}</h2><p style='color:#666'>Gratuit dans l'app comme WhatsApp</p></div>", unsafe_allow_html=True)
        if st.button("📞 LANCER L'APPEL GRATUIT", type="primary", use_container_width=True):
            st.session_state.in_call=True
            components.html("<script>window.parent.playRing();</script>", height=0)
            st.rerun()
    else:
        st.markdown(f"<div style='background:#111;color:white;border-radius:20px;padding:14px;text-align:center'>🔊 En appel • {st.session_state.lang} • Gratuit <span style='color:#25D366'>● En direct</span></div>", unsafe_allow_html=True)
        if st.button("🔴 Raccrocher", use_container_width=True):
            st.session_state.in_call=False
            components.html("<script>window.parent.stopSpeak()</script>", height=0)
            st.rerun()

        components.html(f"""
        <div style="text-align:center;margin-top:12px">
            <button id="mic" style="width:110px;height:110px;border-radius:50%;background:#25D366;color:white;border:none;font-size:40px;cursor:pointer">🎤</button>
            <div id="s" style="margin-top:10px;color:#666;font-size:13px">Clique pour parler en {st.session_state.lang}</div>
            <div id="
