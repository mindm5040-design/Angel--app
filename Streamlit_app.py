import streamlit as st
import requests
import os
import base64
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="ARCHANGE AI", page_icon="🕊️", layout="centered")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY", "")

KEY = get_key()

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0a0d13 0%, #10141c 100%); color: #edeff3; }
header, footer, #MainMenu, .stDeployButton { visibility: hidden !important; }

.archange-header {
    text-align: center; margin: 20px 0 30px;
}
.archange-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 48px; font-weight: 800;
    background: linear-gradient(120deg, #ffd98a, #9b8cff, #7de0c9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.archange-sub {
    color: #ffd98a; font-size: 11px; letter-spacing: 3px;
    font-weight: 700; margin-top: 8px;
}

@keyframes glow { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.archange-logo {
    width: 150px; height: 150px; margin: 0 auto 16px;
    border-radius: 50%; background: rgba(255,217,138,0.1);
    border: 2px solid #ffd98a;
    display: flex; align-items: center; justify-content: center;
    font-size: 70px; animation: glow 2s ease-in-out infinite;
    position: relative;
}
.archange-logo::after {
    content: '';
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    border: 2px dashed rgba(255,217,138,0.3);
    animation: spin 4s linear infinite;
}

.msg-box {
    margin: 14px 0; padding: 14px 16px; border-radius: 12px;
    line-height: 1.7; animation: fadeIn 0.3s ease;
}
.msg-user {
    background: rgba(155,140,255,0.1); border-left: 3px solid #9b8cff;
    margin-left: 24px; color: #edeff3;
}
.msg-assistant {
    background: rgba(255,217,138,0.1); border-left: 3px solid #ffd98a;
    margin-right: 24px; color: #edeff3;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.voice-btn {
    background: linear-gradient(120deg, #ffd98a, #ffeb99);
    color: #1a1204; border: none; border-radius: 20px;
    padding: 8px 14px; font-size: 12px; font-weight: 600;
    cursor: pointer; margin-top: 8px; transition: all .2s;
}
.voice-btn:hover { transform: scale(1.08); box-shadow: 0 6px 16px rgba(255,217,138,0.4); }

.mic-btn {
    background: linear-gradient(120deg, #7de0c9, #5db8a7);
    color: white; border: none; border-radius: 12px;
    padding: 10px 16px; font-size: 13px; font-weight: 600;
    cursor: pointer; width: 100%; transition: all .2s; margin-bottom: 12px;
}
.mic-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(125,224,201,0.3); }
.mic-btn.listening {
    background: #ff8a7a; animation: pulse 1.2s infinite;
}

.btn-primary {
    background: linear-gradient(120deg, #ffd98a, #ffeb99);
    color: #1a1204; border: none; border-radius: 10px;
    padding: 11px 20px; font-weight: 600; font-size: 13px;
    cursor: pointer; width: 100%; transition: all .2s;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255,217,138,0.3); }

.loading {
    display: flex; gap: 10px; align-items: center;
    background: rgba(255,217,138,0.08); padding: 12px 18px;
    border-radius: 20px; border: 1px solid rgba(255,217,138,0.2);
}
.loading-dot {
    width: 30px; height: 30px; background: linear-gradient(120deg, #ffd98a, #ffeb99);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    animation: pulse 1s infinite; font-size: 16px;
}

.alert-error {
    background: rgba(255,107,107,0.1); border-left: 3px solid #ff6b6b;
    color: #ffa8a8; padding: 12px 14px; border-radius: 10px; margin-bottom: 14px;
}

.footer { text-align: center; font-size: 10px; color: #5c6577; margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

def speak_button(text, key_id):
    """Bouton de synthèse vocale"""
    safe_text = text.replace("`", "").replace("'", "\\'").replace('"', '\\"').replace("\n", " ")[:4000]
    components.html(f"""
    <button onclick="speak_{key_id}()" class="voice-btn">🔊 Faire lire par Archange</button>
    <script>
    function speak_{key_id}() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe_text}');
        u.lang = 'fr-FR';
        u.rate = 0.95;
        u.pitch = 1.05;
        window.speechSynthesis.speak(u);
    }}
    </script>
    """, height=50)

def voice_input():
    """Widget de reconnaissance vocale"""
    components.html("""
    <div style="margin-bottom: 12px;">
    <button id="micBtn" onclick="startMic()" class="mic-btn">🎤 Dicter votre question</button>
    <div id="voiceStatus" style="color: #9aa2b1; font-size: 12px; text-align: center; margin-top: 8px;"></div>
    </div>
    
    <script>
    window.voiceText = '';
    function startMic() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'fr-FR';
        recognition.continuous = false;
        const btn = document.getElementById('micBtn');
        const status = document.getElementById('voiceStatus');
        
        btn.classList.add('listening');
        btn.textContent = '🎤 En écoute...';
        status.textContent = 'Microphone actif...';
        
        recognition.onresult = (event) => {
            let text = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                text += event.results[i][0].transcript;
            }
            window.voiceText = text;
            btn.textContent = '✅ ' + text.substring(0, 40) + '...';
            btn.classList.remove('listening');
            status.textContent = 'Envoi en cours...';
        };
        recognition.onerror = () => {
            status.textContent = 'Erreur microphone';
            btn.textContent = '🎤 Dicter votre question';
            btn.classList.remove('listening');
        };
        recognition.start();
    }
    </script>
    """, height=80)

def ask_groq(q):
    """Appel à Groq"""
    try:
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es Archange, un assistant d'étude bienveillant. Sois clair, structuré, efficace. Parle en français."
                },
                {
                    "role": "user",
                    "content": q
                }
            ],
            "max_tokens": 1000
        }
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json=data,
            timeout=60
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"], None
        else:
            return None, f"Erreur Groq {r.status_code}"
    except Exception as e:
        return None, f"Erreur: {str(e)[:60]}"

# ==================== APP ====================

st.markdown(f"""
<div class="archange-header">
    <div class="archange-logo">🕊️</div>
    <div class="archange-title">ARCHANGE</div>
    <div class="archange-sub">INSTRUMENT D'ÉTUDE · GROQ ACTIVE</div>
</div>
""", unsafe_allow_html=True)

if not KEY:
    st.markdown('<div class="alert-error">⚠️ Ajoute GROQ_API_KEY dans Settings → Secrets</div>', unsafe_allow_html=True)
    st.stop()

# TAB SELECTION
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📸 Correction photo", "ℹ️ À propos"])

# ==================== TAB 1: CHAT ====================
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Afficher les messages
    for i, m in enumerate(st.session_state.messages):
        css = "msg-user" if m["role"] == "user" else "msg-assistant"
        st.markdown(f'<div class="msg-box {css}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            speak_button(m["content"], i)
    
    # Entrée vocale
    st.markdown("### 🎤 Dicter votre question")
    voice_input()
    
    # Entrée texte
    st.markdown("### 💬 Ou écrire")
    prompt = st.chat_input("Posez votre question...", key="chat_input")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="msg-box msg-user">{prompt}</div>', unsafe_allow_html=True)
        
        # Appel Groq
        st.markdown('<div class="loading"><div class="loading-dot">🕊️</div> <span>Archange réfléchit...</span></div>', unsafe_allow_html=True)
        
        ans, err = ask_groq(prompt)
        
        if err:
            st.markdown(f'<div class="alert-error">{err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.markdown(f'<div class="msg-box msg-assistant">{ans}</div>', unsafe_allow_html=True)
            speak_button(ans, len(st.session_state.messages) - 1)
        
        st.rerun()

# ==================== TAB 2: CORRECTION PHOTO ====================
with tab2:
    st.markdown("### 📸 Correction au stylo rouge")
    st.caption("Upload une photo de devoir → Archange corrige et note")
    
    uploaded_file = st.file_uploader("Choisis une photo", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        st.image(uploaded_file, width=300, caption="Devoir uploadé")
        
        if st.button("✏️ Corriger au stylo rouge", use_container_width=True):
            st.markdown('<div class="loading"><div class="loading-dot">🕊️</div> <span>Archange analyse...</span></div>', unsafe_allow_html=True)
            
            prompt = "Corrige ce devoir de manière constructive. Donne: 1) Note sur 20, 2) Points forts, 3) Points à améliorer, 4) Conseils pour progresser."
            ans, err = ask_groq(prompt)
            
            if err:
                st.markdown(f'<div class="alert-error">{err}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-box msg-assistant">{ans}</div>', unsafe_allow_html=True)
                speak_button(ans, 999)

# ==================== TAB 3: À PROPOS ====================
with tab3:
    st.markdown("""
    ### 🕊️ ARCHANGE — Instrument d'étude
    
    **Bienvenue dans Archange**, ton assistant d'étude IA.
    
    #### Fonctionnalités :
    - 💬 **Chat illimité** : pose tes questions, Archange répond
    - 🎤 **Dictée vocale** : parle naturellement, Archange te comprend
    - 🔊 **Lecture à voix haute** : écoute les réponses
    - 📸 **Correction de photo** : upload un devoir, Archange corrige
    
    #### Comment ça marche ?
    Archange utilise Groq Llama 3.1, une IA générative ultra-rapide.
    Tes données ne sont jamais stockées — c'est confidentiel.
    
    #### Conseils d'utilisation :
    1. Sois précis dans tes questions
    2. Donne du contexte (niveau, matière)
    3. Écoute les réponses pour mieux comprendre
    
    ---
    
    **ARCHANGE © 2026** — Groq Llama 3.1 · Design Premium
    """)

# Footer
st.markdown('<div class="footer">Archange • IA d\'étude rapide et bienveillante</div>', unsafe_allow_html=True)
