"""
Angel — Instrument d'étude V4
Groq Llama 3.1 • Design Premium • TTS • Version stable
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
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp {
    font-family: 'Inter', -apple-system, sans-serif;
    background: linear-gradient(135deg, #0a0d13 0%, #10141c 50%, #0a0d13 100%);
    color: #edeff3;
}

header, footer, #MainMenu, .stDeployButton { visibility: hidden; }

.angel-header {
    text-align: center; padding: 32px 0;
    background: linear-gradient(180deg, rgba(255,217,138,0.1) 0%, transparent 100%);
    border-bottom: 1px solid rgba(255,217,138,0.2);
    margin-bottom: 24px;
}
.angel-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 48px; font-weight: 800; color: #edeff3; margin: 0;
    background: linear-gradient(120deg, #ffd98a, #9b8cff, #7de0c9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.angel-sub {
    font-size: 11px; letter-spacing: 3px; color: #ffd98a;
    font-weight: 700; margin-top: 8px;
}
.angel-level {
    font-size: 13px; color: #9aa2b1; margin-top: 12px;
    background: rgba(155,140,255,0.05); padding: 10px 16px;
    border-radius: 12px; display: inline-block;
    border: 1px solid rgba(155,140,255,0.15);
}

.mode-tabs {
    display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px;
}
.mode-tab {
    background: rgba(16,20,28,0.8); border: 1px solid rgba(237,239,243,0.15);
    border-radius: 10px; padding: 10px 16px; font-size: 13px; cursor: pointer;
    transition: all .25s; color: #9aa2b1; font-weight: 500;
}
.mode-tab:hover {
    border-color: #ffd98a; color: #ffd98a; background: rgba(255,217,138,0.08);
}
.mode-tab.active {
    border-color: #ffd98a; background: rgba(255,217,138,0.12);
    color: #ffd98a; font-weight: 600;
}

.chat-container {
    max-width: 800px; margin: 0 auto;
}
.chat-msg {
    margin: 14px 0; padding: 14px 16px; border-radius: 12px;
    line-height: 1.7; font-size: 14px;
    animation: fadeIn 0.3s ease-out;
}
.chat-msg.user {
    background: linear-gradient(135deg, rgba(155,140,255,0.1) 0%, rgba(125,224,201,0.05) 100%);
    margin-left: 32px; border-left: 3px solid #9b8cff;
    color: #edeff3;
}
.chat-msg.assistant {
    background: linear-gradient(135deg, rgba(255,217,138,0.1) 0%, rgba(155,140,255,0.05) 100%);
    margin-right: 32px; border-left: 3px solid #ffd98a;
    color: #edeff3;
    box-shadow: 0 2px 8px rgba(255,217,138,0.05);
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.voice-btn {
    background: linear-gradient(120deg, #ffd98a, #ffeb99);
    color: #1a1204; border: none; border-radius: 20px;
    padding: 8px 14px; font-size: 12px; font-weight: 600; cursor: pointer;
    transition: all .2s; margin-top: 8px; display: inline-block;
}
.voice-btn:hover { transform: scale(1.08); box-shadow: 0 6px 16px rgba(255,217,138,0.4); }

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px; font-weight: 700; color: #edeff3;
    margin: 20px 0 14px; display: flex; align-items: center; gap: 8px;
}
.section-title::before {
    content: ""; display: inline-block; width: 3px; height: 20px;
    background: linear-gradient(180deg, #ffd98a, #9b8cff);
    border-radius: 2px;
}

.alert {
    padding: 12px 14px; border-radius: 10px; margin-bottom: 14px;
    font-size: 13px;
}
.alert-error {
    background: rgba(255,107,107,0.1); border-left: 3px solid #ff6b6b;
    color: #ffa8a8;
}
.alert-success {
    background: rgba(34,197,94,0.1); border-left: 3px solid #22c55e;
    color: #86efac;
}

.btn-primary {
    background: linear-gradient(120deg, #ffd98a, #ffeb99);
    color: #1a1204; border: none; border-radius: 10px;
    padding: 11px 20px; font-weight: 600; cursor: pointer;
    font-size: 13px; transition: all .2s;
    width: 100%;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255,217,138,0.3); }

.footer {
    text-align: center; font-size: 11px; color: #5c6577;
    margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(237,239,243,0.1);
}
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
# GROQ API
# ------------------------------------------------------------------
def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")

GROQ_KEY = get_groq_key()

def ask_groq(prompt, level=""):
    """Appel simple à Groq avec gestion d'erreur explicite"""
    if not GROQ_KEY:
        return None, "❌ Clé Groq manquante"
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{
                    "role": "user",
                    "content": f"{prompt} (Niveau: {level})"
                }],
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                return response.json()["choices"][0]["message"]["content"], None
            except:
                return None, "❌ Erreur parsing réponse Groq"
        elif response.status_code == 401:
            return None, "❌ Clé Groq invalide (401)"
        elif response.status_code == 429:
            return None, "❌ Trop de requêtes (429) - attends quelques secondes"
        else:
            return None, f"❌ Groq error {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "❌ Timeout Groq (>30s)"
    except Exception as e:
        return None, f"❌ Erreur: {str(e)[:50]}"

# ------------------------------------------------------------------
# TEXT TO SPEECH
# ------------------------------------------------------------------
def speak_text(txt, btn_id):
    """Crée un bouton pour lire le texte"""
    safe = txt.replace("`", " ").replace("'", " ").replace('"', " ").replace("\n", " ")[:2000]
    html = f"""
    <button onclick='speak{btn_id}()' class='voice-btn'>🔊 Écouter</button>
    <script>
    function speak{btn_id}() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance(`{safe}`);
        u.lang = 'fr-FR';
        u.rate = 0.95;
        u.pitch = 1.05;
        window.speechSynthesis.speak(u);
    }}
    </script>
    """
    components.html(html, height=50)

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
    
    if st.button("🚀 Entrer dans Angel", use_container_width=True):
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
    <div class="angel-level">Niveau: <b>{st.session_state.level}</b> • {st.session_state.get('name', 'Anonyme')}</div>
</div>
""", unsafe_allow_html=True)

if not GROQ_KEY:
    st.markdown('<div class="alert alert-error">⚠️ Clé Groq manquante. Ajoute GROQ_API_KEY dans Settings → Secrets</div>', unsafe_allow_html=True)
    st.stop()

# Mode
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
    st.markdown('<div class="section-title">Conversation d\'étude</div>', unsafe_allow_html=True)
    
    # Afficher les messages existants
    for i, m in enumerate(st.session_state.messages):
        css = "user" if m["role"] == "user" else "assistant"
        st.markdown(f'<div class="chat-msg {css}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            speak_text(m["content"], i)
    
    # Input chat
    p = st.chat_input("Posez votre question...", key="chat_input")
    if p:
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": p})
        st.markdown(f'<div class="chat-msg user">{p}</div>', unsafe_allow_html=True)
        
        # Appeler Groq
        with st.spinner("⏳ Groq réfléchit…"):
            ans, err = ask_groq(p, st.session_state.level)
        
        # Afficher résultat ou erreur
        if err:
            st.markdown(f'<div class="alert alert-error">{err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.markdown(f'<div class="chat-msg assistant">{ans}</div>', unsafe_allow_html=True)
            speak_text(ans, len(st.session_state.messages) - 1)
        
        st.rerun()

# ------------------------------------------------------------------
# MODE 2: CORRECTION PHOTO
# ------------------------------------------------------------------
elif mode == "📸 Correction photo":
    st.markdown('<div class="section-title">Correction au stylo rouge</div>', unsafe_allow_html=True)
    st.caption("Upload une photo de devoir → Angel corrige et note")
    
    img = st.file_uploader("Upload photo", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    if img:
        st.image(img, width=280)
        
        if st.button("✏️ Corriger", use_container_width=True):
            with st.spinner("Analyse…"):
                prompt = f"Corrige ce devoir niveau {st.session_state.level}. Note/20, points forts, points faibles, conseils."
                ans, err = ask_groq(prompt, st.session_state.level)
            
            if err:
                st.markdown(f'<div class="alert alert-error">{err}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg assistant">{ans}</div>', unsafe_allow_html=True)
                speak_text(ans, 900)

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
    
    if st.button("📋 Générer", use_container_width=True):
        with st.spinner("Génération…"):
            prompt = f"Fiche révision {st.session_state.level} - {mat} - {chap}: définitions, résumé, exemples, 3 exercices"
            ans, err = ask_groq(prompt, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">{err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(ans)
            speak_text(ans, 901)
            st.download_button("💾 Télécharger", ans, file_name=f"Angel_{chap}.txt", use_container_width=True)

# ------------------------------------------------------------------
# MODE 4: EXAMEN BLANC
# ------------------------------------------------------------------
elif mode == "🧪 Examen blanc":
    st.markdown('<div class="section-title">Examen blanc 10 questions</div>', unsafe_allow_html=True)
    
    if st.button("🎯 Démarrer", use_container_width=True):
        with st.spinner("Génération…"):
            prompt = f"Génère 10 QCM niveau {st.session_state.level}. Format: Question 1) A) B) C) D) ..."
            qs, err = ask_groq(prompt, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">{err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.exam_questions = qs
            st.markdown(qs)
    
    if st.session_state.exam_questions:
        rep = st.text_input("Tes réponses", placeholder="1A 2B 3C…")
        
        if st.button("✅ Corriger", use_container_width=True):
            if not rep.strip():
                st.warning("Entre au moins une réponse")
            else:
                with st.spinner("Correction…"):
                    prompt = f"Corrige: {st.session_state.exam_questions} Réponses: {rep} Note/20, bonnes réponses, explications"
                    ans, err = ask_groq(prompt, st.session_state.level)
                
                if err:
                    st.markdown(f'<div class="alert alert-error">{err}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg assistant">{ans}</div>', unsafe_allow_html=True)
                    st.balloons()
                    speak_text(ans, 902)

# ------------------------------------------------------------------
# MODE 5: EXERCICE GUIDÉ
# ------------------------------------------------------------------
elif mode == "📚 Exercice guidé":
    st.markdown('<div class="section-title">Exercice pas à pas</div>', unsafe_allow_html=True)
    
    mat = st.selectbox("Matière", SUBJECTS, label_visibility="collapsed")
    
    if st.button("📖 Générer", use_container_width=True):
        with st.spinner("Création…"):
            prompt = f"Crée 1 exercice {st.session_state.level} en {mat}: ÉNONCÉ → ÉTAPES → SOLUTION"
            ans, err = ask_groq(prompt, st.session_state.level)
        
        if err:
            st.markdown(f'<div class="alert alert-error">{err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(ans)
            speak_text(ans, 903)

# Footer
st.markdown("""
<div class="footer">
Angel © 2026 · Groq Llama 3.1 · Design Premium · TTS
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.level = None
        st.session_state.messages = []
        st.session_state.exam_questions = ""
        st.rerun()
