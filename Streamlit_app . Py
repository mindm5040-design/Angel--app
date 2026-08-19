"""
Angel — Instrument d'étude
MVP déployable sur Streamlit Community Cloud (share.streamlit.io).
Tous les appels aux moteurs IA se font côté serveur Python (pas de fetch
navigateur) : aucun blocage CORS possible, contrairement à la version HTML pure.
"""

import io
import time
import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

# ------------------------------------------------------------------
# CONFIG PAGE
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Angel — Instrument d'étude",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# DESIGN — CSS injecté
# ------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root{
  --obsidian:#0a0d13; --panel:#10141c; --panel2:#151a24;
  --line: rgba(237,239,243,0.10); --line-strong: rgba(237,239,243,0.18);
  --ink:#edeff3; --ink-dim:#9aa2b1; --ink-faint:#5c6577;
  --halo:#ffd98a; --halo-dim: rgba(255,217,138,0.14);
  --violet:#9b8cff; --violet-dim: rgba(155,140,255,0.14);
}

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
.stApp{
  background:
    radial-gradient(1200px 600px at 15% -10%, rgba(255,217,138,0.06), transparent 60%),
    radial-gradient(1000px 700px at 105% 10%, rgba(155,140,255,0.07), transparent 55%),
    var(--obsidian);
  color: var(--ink);
}
section[data-testid="stSidebar"]{
  background: var(--panel); border-right: 1px solid var(--line);
}
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing:-0.01em; }
.mono { font-family:'IBM Plex Mono', monospace; }

.angel-eyebrow{
  color: var(--ink-faint); font-size:12px; letter-spacing:0.18em; text-transform:uppercase;
  display:flex; align-items:center; gap:10px; margin-bottom:18px;
}
.angel-eyebrow .dash{ width:28px; height:1px; background: var(--line-strong); display:inline-block;}
.angel-accent{ color: var(--halo); }

.choice-box{
  background: var(--panel2); border:1px solid var(--line); border-radius:14px;
  padding:20px 22px; margin-bottom:10px; transition: border-color .15s;
}
.choice-box:hover{ border-color: var(--line-strong); }
.choice-title{ font-family:'Space Grotesk'; font-weight:600; font-size:17px; margin-bottom:4px;}
.choice-desc{ color: var(--ink-dim); font-size:13px; line-height:1.5;}

.profile-strip{
  background: var(--panel2); border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin-bottom:14px;
  font-size:12.5px;
}
.profile-strip .row{ display:flex; justify-content:space-between; margin-bottom:5px;}
.profile-strip .row:last-child{ margin-bottom:0;}
.profile-strip .lbl{ color: var(--ink-faint);}
.profile-strip .val{ color: var(--ink); font-weight:600;}
.plan-free{ color: var(--halo) !important; }
.plan-premium{ color: var(--violet) !important; }

.tag{
  display:inline-block; font-size:11px; padding:4px 9px; border:1px solid var(--line);
  border-radius:20px; color: var(--ink-dim); margin:0 6px 6px 0;
}

.fusion-tag{
  font-family:'IBM Plex Mono'; font-size:10.5px; color: var(--ink-faint); margin-top:6px;
}
.fusion-tag span{ padding:2px 6px; border:1px solid var(--line); border-radius:5px; margin-right:6px;}

/* boutons Streamlit -> style halo */
.stButton>button{
  background: var(--panel2); color: var(--ink); border:1px solid var(--line);
  border-radius:10px; padding:10px 18px; font-weight:600; transition: all .15s;
}
.stButton>button:hover{ border-color: var(--halo); color: var(--halo); }
div[data-testid="stChatInput"] textarea{ background: var(--panel2) !important; color: var(--ink) !important; }

/* halo ring animé (svg statique + rotation css) */
.halo-ring{ width:70px; height:70px; margin: 0 auto 18px; }
.halo-ring svg{ animation: halo-spin 3.2s linear infinite; }
@keyframes halo-spin{ to{ transform: rotate(360deg); } }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

HALO_SVG = """
<div class="halo-ring">
<svg viewBox="0 0 64 64" width="70" height="70">
  <circle cx="32" cy="32" r="26" fill="none" stroke="rgba(237,239,243,0.18)" stroke-width="1.4"/>
  <circle cx="32" cy="32" r="9" fill="#10141c" stroke="rgba(237,239,243,0.18)"/>
  <path d="M32 6 A26 26 0 0 1 55 20" fill="none" stroke="#ffd98a" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M9 20 A26 26 0 0 1 20 8" fill="none" stroke="#9b8cff" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M40 57 A26 26 0 0 1 12 45" fill="none" stroke="#7de0c9" stroke-width="2.4" stroke-linecap="round"/>
</svg>
</div>
"""

# ------------------------------------------------------------------
# DONNÉES
# ------------------------------------------------------------------
LEVELS_COLLEGE = ["6e", "5e", "4e", "3e", "Seconde", "Première", "Terminale"]
LEVELS_UNIV = ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
SUBJECTS_COLLEGE = ["Maths", "Physique-Chimie", "SVT", "Français", "Anglais", "Histoire-Géo", "Philosophie", "Informatique"]
SUBJECTS_UNIV = ["Analyse", "Algèbre", "Physique", "Droit", "Économie", "Informatique", "Méthodologie", "Rédaction académique"]
CHIPS_COLLEGE = ["Explique-moi les fractions", "Résume ce chapitre d'Histoire", "Corrige ma dissertation", "Prépare-moi à l'interrogation"]
CHIPS_UNIV = ["Démontre ce théorème", "Structure mon plan de mémoire", "Vérifie ce raisonnement", "Synthétise cet article"]

SYSTEM_PROMPT_BASE = """Tu es Angel, un instrument d'étude exclusivement académique. Règles strictes :
1. Ton direct, sans humour, sans small talk, sans formules de politesse superflues.
2. Efficacité maximale : réponse structurée, dense, sans remplissage.
3. Sensibilité psychologique : tu perçois quand l'élève est en difficulté, stressé ou en surcharge, et tu ajustes ton rythme sans jamais le materner ni le flatter artificiellement.
4. Exclusivement scolaire/académique : tu refuses poliment tout sujet hors études.
5. Tu t'adaptes strictement au niveau déclaré de l'élève."""

# ------------------------------------------------------------------
# ÉTAT DE SESSION
# ------------------------------------------------------------------
defaults = {
    "step": 1, "cycle": None, "level": None, "first_name": "",
    "plan": "gratuit", "voice_on": False, "messages": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def get_keys():
    """Priorité aux Secrets Streamlit (déploiement), sinon saisie manuelle en sidebar."""
    claude = st.secrets.get("ANTHROPIC_API_KEY", "") or st.session_state.get("key_claude", "")
    openai_k = st.secrets.get("OPENAI_API_KEY", "") or st.session_state.get("key_openai", "")
    gemini = st.secrets.get("GEMINI_API_KEY", "") or st.session_state.get("key_gemini", "")
    return claude, openai_k, gemini


def build_system_prompt():
    cycle_txt = "secondaire" if st.session_state.cycle == "college" else "supérieur"
    prompt = SYSTEM_PROMPT_BASE + f"\nNiveau de l'élève : {st.session_state.level} ({cycle_txt})."
    if st.session_state.first_name:
        prompt += f"\nPrénom de l'élève : {st.session_state.first_name}."
    return prompt


# ------------------------------------------------------------------
# APPELS MOTEURS (SERVEUR — pas de CORS possible ici)
# ------------------------------------------------------------------
def call_claude(question, key):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 900,
            "system": build_system_prompt(),
            "messages": [{"role": "user", "content": question}],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return "".join(b.get("text", "") for b in data.get("content", [])).strip()


def call_openai(question, key):
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4.1",
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": question},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()


def call_gemini(question, key):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
        json={
            "systemInstruction": {"parts": [{"text": build_system_prompt()}]},
            "contents": [{"role": "user", "parts": [{"text": question}]}],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    parts = data["candidates"][0]["content"]["parts"]
    return "\n".join(p.get("text", "") for p in parts).strip()


def fuse_answer(question):
    kC, kO, kG = get_keys()
    jobs = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        if kC:
            jobs[pool.submit(call_claude, question, kC)] = "CLAUDE"
        if kO:
            jobs[pool.submit(call_openai, question, kO)] = "GPT"
        if kG:
            jobs[pool.submit(call_gemini, question, kG)] = "GEMINI"

        if not jobs:
            raise RuntimeError("Aucune clé API renseignée. Ajoutez vos clés dans la barre latérale.")

        results, errors = {}, {}
        for future in as_completed(jobs):
            engine = jobs[future]
            try:
                results[engine] = future.result()
            except Exception as e:
                errors[engine] = str(e)

    if not results:
        raise RuntimeError(" · ".join(f"{k}: {v}" for k, v in errors.items()))

    primary_engine = "CLAUDE" if "CLAUDE" in results else next(iter(results))
    return results[primary_engine], list(results.keys())


def speak(text):
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="fr").write_to_fp(buf)
        buf.seek(0)
        st.audio(buf, format="audio/mp3", autoplay=True)
    except Exception:
        pass  # la voix est un bonus, jamais bloquant


def transcribe_audio(audio_bytes, key):
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"model": "whisper-1", "language": "fr"}
    r = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {key}"},
        files=files, data=data, timeout=60,
    )
    r.raise_for_status()
    return r.json().get("text", "")


# ------------------------------------------------------------------
# ONBOARDING
# ------------------------------------------------------------------
def render_onboarding():
    st.markdown('<div class="angel-eyebrow"><span class="dash"></span> ANGEL · INSTRUMENT D\'ÉTUDE <span class="dash"></span></div>', unsafe_allow_html=True)

    if st.session_state.step == 1:
        st.markdown("## Choisissez votre <span class='angel-accent'>cycle</span>.", unsafe_allow_html=True)
        st.caption("Angel calibre chaque réponse sur votre niveau réel.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="choice-box"><div class="choice-title">Collège &amp; Lycée</div>'
                        '<div class="choice-desc">De la 6e à la Terminale.</div></div>', unsafe_allow_html=True)
            if st.button("Choisir Collège & Lycée", use_container_width=True):
                st.session_state.cycle = "college"
                st.session_state.step = 2
                st.rerun()
        with c2:
            st.markdown('<div class="choice-box"><div class="choice-title">Université</div>'
                        '<div class="choice-desc">Licence, Master, Doctorat.</div></div>', unsafe_allow_html=True)
            if st.button("Choisir Université", use_container_width=True):
                st.session_state.cycle = "universite"
                st.session_state.step = 2
                st.rerun()

    elif st.session_state.step == 2:
        st.markdown("## Votre <span class='angel-accent'>classe</span>.", unsafe_allow_html=True)
        levels = LEVELS_COLLEGE if st.session_state.cycle == "college" else LEVELS_UNIV
        cols = st.columns(4)
        for i, lv in enumerate(levels):
            with cols[i % 4]:
                if st.button(lv, key=f"lv_{lv}", use_container_width=True):
                    st.session_state.level = lv
                    st.session_state.step = 3
                    st.rerun()
        if st.button("← Retour"):
            st.session_state.step = 1
            st.rerun()

    elif st.session_state.step == 3:
        st.markdown("## Votre <span class='angel-accent'>formule</span>.", unsafe_allow_html=True)
        st.session_state.first_name = st.text_input("Prénom (optionnel)", value=st.session_state.first_name)
        plan = st.radio(
            "Formule",
            ["gratuit", "premium"],
            format_func=lambda x: "Gratuit — usage limité / jour" if x == "gratuit" else "Premium (Angel+) — priorité, voix illimitée",
            horizontal=True,
        )
        st.session_state.plan = plan
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Retour"):
                st.session_state.step = 2
                st.rerun()
        with c2:
            if st.button("Entrer dans Angel →", type="primary", use_container_width=True):
                st.session_state.step = 4
                st.rerun()


# ------------------------------------------------------------------
# APPLICATION PRINCIPALE
# ------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🕊️ Angel")
        st.caption("fusion tutoring engine")

        plan_class = "plan-premium" if st.session_state.plan == "premium" else "plan-free"
        plan_label = "Angel+ Premium" if st.session_state.plan == "premium" else "Gratuit"
        st.markdown(f"""
        <div class="profile-strip">
          <div class="row"><span class="lbl">Élève</span><span class="val">{st.session_state.first_name or "Anonyme"}</span></div>
          <div class="row"><span class="lbl">Niveau</span><span class="val">{st.session_state.level}</span></div>
          <div class="row"><span class="lbl">Formule</span><span class="val {plan_class}">{plan_label}</span></div>
        </div>
        """, unsafe_allow_html=True)

        subjects = SUBJECTS_COLLEGE if st.session_state.cycle == "college" else SUBJECTS_UNIV
        st.markdown("".join(f'<span class="tag">{s}</span>' for s in subjects), unsafe_allow_html=True)

        st.divider()
        st.session_state.voice_on = st.toggle("🔊 Mode vocal (réponses parlées)", value=st.session_state.voice_on)

        with st.expander("🔑 Clés API & moteurs"):
            st.caption("Priorité aux Secrets Streamlit si configurés. Sinon, saisissez vos clés ici (non persistées entre sessions).")
            st.session_state["key_claude"] = st.text_input("Anthropic (Claude)", type="password", value=st.session_state.get("key_claude", ""))
            st.session_state["key_openai"] = st.text_input("OpenAI (GPT / Whisper)", type="password", value=st.session_state.get("key_openai", ""))
            st.session_state["key_gemini"] = st.text_input("Google (Gemini)", type="password", value=st.session_state.get("key_gemini", ""))

        st.divider()
        if st.button("Nouvelle conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.button("Changer de niveau", use_container_width=True):
            st.session_state.step = 1
            st.session_state.messages = []
            st.rerun()


def render_chat():
    st.markdown(f"#### Session — {st.session_state.first_name or 'étude'}")
    st.caption("CLAUDE · GPT · GEMINI — fusion active · ton direct, méthodique, sans détour")

    if not st.session_state.messages:
        st.markdown(HALO_SVG, unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; color:#9aa2b1; margin-bottom:18px;'>Posez votre première question.</div>", unsafe_allow_html=True)
        chips = CHIPS_COLLEGE if st.session_state.cycle == "college" else CHIPS_UNIV
        cols = st.columns(len(chips))
        for i, c in enumerate(chips):
            with cols[i]:
                if st.button(c, key=f"chip_{i}", use_container_width=True):
                    handle_question(c)
                    st.rerun()

    for m in st.session_state.messages:
        avatar = "🕊️" if m["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(m["role"], avatar=avatar):
            st.write(m["content"])
            if m["role"] == "assistant" and m.get("engines"):
                st.markdown('<div class="fusion-tag">' + "".join(f"<span>{e}</span>" for e in m["engines"]) + "</div>", unsafe_allow_html=True)

    # Entrée vocale (optionnelle)
    kC, kO, kG = get_keys()
    if kO:
        audio = st.audio_input("Dicter une question")
        if audio is not None and st.button("Envoyer l'audio", key="send_audio"):
            with st.spinner("Transcription…"):
                try:
                    text = transcribe_audio(audio.read(), kO)
                    if text:
                        handle_question(text)
                        st.rerun()
                except Exception as e:
                    st.error(f"Transcription impossible : {e}")

    prompt = st.chat_input("Écrivez votre question de cours…")
    if prompt:
        handle_question(prompt)
        st.rerun()


def handle_question(question):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Fusion en cours — Claude · GPT · Gemini…"):
        try:
            text, engines = fuse_answer(question)
        except Exception as e:
            text, engines = f"Erreur de fusion : {e}", []
    st.session_state.messages.append({"role": "assistant", "content": text, "engines": engines})
    if st.session_state.voice_on and engines:
        speak(text)


# ------------------------------------------------------------------
# ROUTAGE
# ------------------------------------------------------------------
if st.session_state.step < 4:
    render_onboarding()
else:
    render_sidebar()
    render_chat()
    
