"""
Angel — Instrument d'étude (Groq Edition)
Version simple avec une seule clé API (Groq).
Modes: Chat, Correction photo, Fiche révision, Examen blanc, Exercices.
"""

import streamlit as st
import requests
import os
import streamlit.components.v1 as components

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Angel — Instrument d'étude",
    page_icon="🕊️",
    layout="centered",
)

st.markdown("""
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body, html { font-family: 'Inter', -apple-system, sans-serif; background: #FCFCF9; }
.stApp { background: #FCFCF9; }
header, footer, #MainMenu, .stDeployButton { visibility: hidden; }

.angel-header {
    text-align: center; padding: 24px 0;
    border-bottom: 1px solid #eee; margin-bottom: 24px;
}
.angel-title {
    font-size: 42px; font-weight: 800; color: #0a0d13; margin: 0;
}
.angel-sub {
    font-size: 11px; letter-spacing: 2px; color: #ffd98a; 
    font-weight: 700; margin-top: 6px;
}
.angel-level {
    font-size: 12px; color: #999; margin-top: 8px;
}

.mode-tabs {
    display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px;
}
.mode-tab {
    background: white; border: 1px solid #e0e0e0; border-radius: 10px;
    padding: 8px 14px; font-size: 13px; cursor: pointer;
    transition: all .2s; color: #666;
}
.mode-tab:hover, .mode-tab.active {
    border-color: #ffd98a; background: #fffaf5; color: #0a0d13; font-weight: 600;
}

.chat-msg { margin: 12px 0; padding: 12px 14px; border-radius: 10px; line-height: 1.6; }
.chat-msg.user { background: #f5f5f5; margin-left: 24px; border-left: 3px solid #e0e0e0; }
.chat-msg.assistant {
    background: #fffaf5; margin-right: 24px; border-left: 3px solid #ffd98a;
    color: #0a0d13;
}

.voice-btn {
    background: #ffd98a; color: #1a1204; border: none; border-radius: 20px;
    padding: 6px 12px; font-size: 11px; font-weight: 600; cursor: pointer;
    transition: all .2s; margin-top: 8px;
}
.voice-btn:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(255,217,138,0.3); }

.section-title { font-size: 16px; font-weight: 700; color: #0a0d13; margin: 16px 0 12px; }
.input-group { margin-bottom: 16px; }
.input-group label { font-size: 12px; font-weight: 600; color: #999; display: block; margin-bottom: 6px; }

.alert { padding: 12px; border-radius: 10px; margin-bottom: 16px; font-size: 13px; }
.alert-error { background: #fff5f5; border-left: 3px solid #ff6b6b; color: #c92a2a; }
.alert-success { background: #f0fdf4; border-left: 3px solid #22c55e; color: #166534; }

.footer { text-align: center; font-size: 10px; color: #ccc; margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DATA
# ------------------------------------------------------------------
LEVELS = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["L1", "L2", "L3", "M1", "M2", "Doctorat"]
}
SUBJECTS = ["Maths", "Physique-Chimie", "SVT", "Français", "Anglais", "Histoire-Géo", "Philosophie", "Informatique"]

# ------------------------------------------------------------------
# GET API KEY
# ------------------------------------------------------------------
def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")

GROQ_KEY = get_groq_key()

# ------------------------------------------------------------------
# GROQ CALL
# ------------------------------------------------------------------
def ask_groq(prompt, level=""):
    if not GROQ_KEY:
        return None, "Clé Groq manquante"
    
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "user",
                        "content": f"{prompt} (Niveau: {level}). Sois direct, structuré, sans humour."
                    }
                ]
            },
            timeout=20
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"], None
        else:
            return None, f"Groq: {r.status_code}"
    except requests.exceptions.Timeout:
        return None, "Timeout Groq (>20s)"
    except Exception as e:
        return None, str(e)

# ------------------------------------------------------------------
# TEXT TO SPEECH
# ------------------------------------------------------------------
def speak_btn(txt, kid):
    safe = txt.replace("`", " ").replace("'", " ").replace('"', " ").replace("\n", " ")[:1500]
    html = f"""
    <button onclick='s{kid}()' class='voice-btn'>🔊 Écouter</button>
    <script>
    function s{kid}() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance(`{safe}`);
        u.lang = 'fr-FR';
        u.rate = 1.0;
        window.speechSynthesis.speak(u);
    }}
    </script>
    """
    components.html(html, height=45)

# ------------------------------------------------------------------
# STATE
# ------------------------------------------------------------------
if "level" not in st.session_state:
    st.session_state.level = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = ""

# ------------------------------------------------------------------
# ONBOARDING
# ------------------------------------------------------------------
if not st.session_state.level:
    st.markdown("""
    <div class="angel-header">
        <div class="angel-title">🕊️ Angel</div>
        <div class="angel-sub">INSTRUMENT D'ÉTUDE — GROQ LLAMA 3.1</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        cycle = st.radio("**Cycle**", list(LEVELS.keys()), label_visibility="collapsed")
    with col2:
        level = st.selectbox("**Classe**", LEVELS[cycle], label_visibility="collapsed")
    
    name = st.text_input("**Prénom (optionnel)**", label_visibility="collapsed", placeholder="Ex. Aïcha")
    
    if st.button("🚀 Entrer dans Angel", use_container_width=True, type="primary"):
        st.session_state.level = level
        st.session_state.name = name or "Élève"
        st.rerun()
    st.stop()

# ------------------------------------------------------------------
# MAIN APP
# ------------------------------------------------------------------
st.markdown(f"""
<div class="angel-header">
    <div class="angel-title">🕊️ Angel</div>
    <div class="angel-level">Niveau: <b>{st.session_state.level}</b> • Utilisateur: <b>{st.session_state.get('name', 'Anonyme')}</b></div>
</div>
""", unsafe_allow_html=True)

if not GROQ_KEY:
    st.markdown('<div class="alert alert-error">⚠️ Clé Groq manquante. Ajoute GROQ_API_KEY dans Settings → Secrets</div>', unsafe_allow_html=True)
    st.stop()

# Mode selection
mode = st.radio(
    "Mode",
    ["💬 Chat", "📸 Correction photo", "📝 Fiche révision", "🧪 Examen blanc", "📚 Exercice guidé"],
    horizontal=True,
    label_visibility="collapsed"
)

# ------------------------------------------------------------------
# MODE 1: CHAT
# ------------------------------------------------------------------
if mode == "💬 Chat":
    st.markdown('<div class="section-title">Conversation</div>', unsafe_allow_html=True)
    
    for i, m in enumerate(st.session_state.messages):
        css = "user" if m["role"] == "user" else "assistant"
        st.markdown(f'<div class="chat-msg {css}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            speak_btn(m["content"], i)
    
    p = st.chat_input("Votre question...", key="chat_input")
    if p:
        st.session_state.messages.append({"role": "user", "content": p})
        st.markdown(f'<div class="chat-msg user">{p}</div>', unsafe_allow_html=True)
        
        with st.spinner("Réflexion en cours…"):
            ans, err = ask_groq(p, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">❌ {err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.markdown(f'<div class="chat-msg assistant">{ans}</div>', unsafe_allow_html=True)
            speak_btn(ans, len(st.session_state.messages))
        st.rerun()

# ------------------------------------------------------------------
# MODE 2: CORRECTION PHOTO
# ------------------------------------------------------------------
elif mode == "📸 Correction photo":
    st.markdown('<div class="section-title">Correction au stylo rouge</div>', unsafe_allow_html=True)
    st.caption("Prends une photo de ton devoir → Angel corrige et note")
    
    img = st.file_uploader("Upload photo", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    if img:
        st.image(img, width=250, caption="Devoir uploadé")
        
        if st.button("✏️ Corriger au stylo rouge", use_container_width=True):
            with st.spinner("Analyse et correction…"):
                prompt = f"Corrige ce devoir niveau {st.session_state.level}. Donne: note/20, points forts, points faibles, conseils d'amélioration."
                ans, err = ask_groq(prompt, st.session_state.level)
            
            if err:
                st.markdown(f'<div class="alert alert-error">❌ {err}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg assistant">{ans}</div>', unsafe_allow_html=True)
                speak_btn(ans, 900)

# ------------------------------------------------------------------
# MODE 3: FICHE RÉVISION
# ------------------------------------------------------------------
elif mode == "📝 Fiche révision":
    st.markdown('<div class="section-title">Générer fiche révision</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        mat = st.selectbox("Matière", SUBJECTS, label_visibility="collapsed")
    with col2:
        chap = st.text_input("Chapitre", "Réplication ADN", label_visibility="collapsed")
    
    if st.button("📋 Générer fiche", use_container_width=True, type="primary"):
        with st.spinner("Génération…"):
            prompt = f"Fiche révision niveau {st.session_state.level} - {mat} - {chap}. Format: 1) Définitions clés, 2) Résumé, 3) Exemples, 4) 3 exercices corrigés"
            ans, err = ask_groq(prompt, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">❌ {err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(ans)
            speak_btn(ans, 901)
            st.download_button("💾 Télécharger", ans, file_name=f"Angel_{chap}.txt", use_container_width=True)

# ------------------------------------------------------------------
# MODE 4: EXAMEN BLANC
# ------------------------------------------------------------------
elif mode == "🧪 Examen blanc":
    st.markdown('<div class="section-title">Examen blanc 10 questions</div>', unsafe_allow_html=True)
    
    if st.button("🎯 Démarrer examen", use_container_width=True, type="primary"):
        with st.spinner("Génération des questions…"):
            prompt = f"Génère 10 QCM niveau {st.session_state.level}. Format strict: Question 1) A) ... B) ... C) ... D) ... Question 2) etc."
            qs, err = ask_groq(prompt, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">❌ {err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.exam_questions = qs
            st.markdown(qs)
    
    if st.session_state.exam_questions:
        rep = st.text_input("Tes réponses (ex: 1A 2B 3C…)", key="exam_answers", placeholder="1A 2C 3B...")
        
        if st.button("✅ Corriger et noter", use_container_width=True):
            if not rep.strip():
                st.warning("Rentre au moins une réponse")
            else:
                with st.spinner("Correction…"):
                    prompt = f"Corrige ce QCM.\nQuestions:\n{st.session_state.exam_questions}\nRéponses élève: {rep}\nDonne: note/20, réponses correctes, explications."
                    ans, err = ask_groq(prompt, st.session_state.level)
                
                if err:
                    st.markdown(f'<div class="alert alert-error">❌ {err}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg assistant">{ans}</div>', unsafe_allow_html=True)
                    st.balloons()
                    speak_btn(ans, 902)

# ------------------------------------------------------------------
# MODE 5: EXERCICE GUIDÉ
# ------------------------------------------------------------------
elif mode == "📚 Exercice guidé":
    st.markdown('<div class="section-title">Exercice pas à pas</div>', unsafe_allow_html=True)
    
    mat = st.selectbox("Matière", SUBJECTS, label_visibility="collapsed")
    
    if st.button("📖 Générer exercice", use_container_width=True, type="primary"):
        with st.spinner("Création…"):
            prompt = f"Crée 1 exercice niveau {st.session_state.level} en {mat}. Format: ÉNONCÉ → ÉTAPES (3-4 étapes) → SOLUTION COMPLÈTE"
            ans, err = ask_groq(prompt, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">❌ {err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(ans)
            speak_btn(ans, 903)

# ------------------------------------------------------------------
# FOOTER & SIDEBAR
# ------------------------------------------------------------------
st.markdown("""
<div class="footer">
Angel © 2026 — Groq Llama 3.1 · Instrument d'étude autonome
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("🔄 Réinitialiser"):
        st.session_state.level = None
        st.session_state.messages = []
        st.session_state.exam_questions = ""
        st.rerun()
