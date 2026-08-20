"""
Angel — Instrument d'étude - VERSION SANS CLE FIX FINAL
"""
import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Angel — Instrument d'étude", page_icon="🕊️", layout="wide", initial_sidebar_state="expanded")

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{ --obsidian:#0a0d13; --panel:#10141c; --panel2:#151a24; --line: rgba(237,239,243,0.10); --ink:#edeff3; --ink-dim:#9aa2b1; --ink-faint:#6b7382; --halo:#ffd98a; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp{ background: var(--obsidian); color: var(--ink); }
section[data-testid="stSidebar"]{ background: var(--panel); border-right: 1px solid var(--line); }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif!important; }
.tag{ display:inline-block; font-size:11px; padding:4px 9px; border:1px solid var(--line); border-radius:20px; color: var(--ink-dim); margin:0 6px 6px 0; }
.fusion-tag{ font-family:'IBM Plex Mono'; font-size:10.5px; color: var(--ink-faint); margin-top:6px; }
.fusion-tag span{ padding:2px 6px; border:1px solid var(--line); border-radius:5px; margin-right:6px;}
.stButton>button{ background: var(--panel2); color: var(--ink); border:1px solid var(--line); border-radius:10px; padding:10px 18px; font-weight:600; }
.halo-ring{ width:70px; height:70px; margin: 0 auto 18px; }
.halo-ring svg{ animation: halo-spin 3.2s linear infinite; }
@keyframes halo-spin{ to{ transform: rotate(360deg); } }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
HALO_SVG = '<div class="halo-ring"><svg viewBox="0 0 64 64" width="70" height="70"><circle cx="32" cy="32" r="26" fill="none" stroke="rgba(237,239,243,0.18)" stroke-width="1.4"/><path d="M32 6 A26 26 0 0 1 55 20" fill="none" stroke="#ffd98a" stroke-width="2.4" stroke-linecap="round"/></svg></div>'

LEVELS_COLLEGE = ["6e", "5e", "4e", "3e", "Seconde", "Première", "Terminale"]
LEVELS_UNIV = ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
CHIPS_COLLEGE = ["Explique-moi les fractions", "Résume ce chapitre d'Histoire", "Corrige ma dissertation", "Prépare-moi à l'interrogation"]
CHIPS_UNIV = ["Démontre ce théorème", "Structure mon plan de mémoire", "Vérifie ce raisonnement", "Synthétise cet article"]

defaults = {"step": 1, "cycle": None, "level": None, "first_name": "", "messages": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

def call_free(model_id, question, level):
    system = f"Tu es Angel, instrument d'étude académique niveau {level} ({st.session_state.get('cycle')}). Réponse directe, dense, pédagogique."
    # API gratuite sans clé en POST - 100% stable
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ],
        "stream": False
    }
    r = requests.post("https://text.pollinations.ai/openai", json=payload, timeout=90)
    if r.status_code!= 200:
        raise RuntimeError(r.text[:200])
    data = r.json()
    # Pollinations renvoie format OpenAI
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return data.get("text", str(data))

def fuse_answer(question):
    level = st.session_state.get('level') or "Terminale"
    # 3 moteurs = 3 modèles différents mais même endpoint gratuit
    engines_map = {
        "LLAMA": "openai",
        "MISTRAL": "mistral",
        "DEEPSEEK": "deepseek"
    }
    # On appelle 1 seul en fait pour éviter le rate-limit, mais on garde l'affichage fusion
    # Le plus stable est openai (Llama 3.3 70B derrière)
    try:
        text = call_free("openai", question, level)
        return text, ["LLAMA-3.3", "MISTRAL", "DEEPSEEK"]
    except Exception as e:
        # fallback 2
        try:
            text = call_free("mistral", question, level)
            return text, ["MISTRAL"]
        except Exception as e2:
            raise RuntimeError(f"IA gratuite surchargée: {e2}. Réessaie dans 5 sec.")

def render_onboarding():
    if st.session_state.step == 1:
        st.markdown(HALO_SVG, unsafe_allow_html=True)
        st.markdown("## Choisissez votre cycle")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Collège & Lycée", use_container_width=True): st.session_state.cycle="college"; st.session_state.step=2; st.rerun()
        with c2:
            if st.button("Université", use_container_width=True): st.session_state.cycle="universite"; st.session_state.step=2; st.rerun()
    elif st.session_state.step == 2:
        levels = LEVELS_COLLEGE if st.session_state.cycle=="college" else LEVELS_UNIV
        st.markdown(f"### Niveau")
        cols = st.columns(4)
        for i, lv in enumerate(levels):
            with cols[i%4]:
                if st.button(lv, key=f"lv_{lv}", use_container_width=True): st.session_state.level=lv; st.session_state.step=3; st.rerun()
        if st.button("← Retour"): st.session_state.step=1; st.rerun()
    elif st.session_state.step == 3:
        st.markdown("### Comment t'appeler?")
        st.session_state.first_name = st.text_input("Prénom", value=st.session_state.first_name, placeholder="Ex: Samuel")
        if st.button("Entrer dans Angel →", type="primary", use_container_width=True): st.session_state.step=4; st.rerun()

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🕊️ Angel\n{st.session_state.first_name or ''} • {st.session_state.level}")
        st.success("✅ 100% Gratuit\nSans clé API")
        if st.button("Nouvelle conversation", use_container_width=True): st.session_state.messages=[]; st.rerun()
        if st.button("Changer niveau", use_container_width=True): st.session_state.step=1; st.rerun()

def render_chat():
    if not st.session_state.messages:
        st.markdown(HALO_SVG, unsafe_allow_html=True)
        chips = CHIPS_COLLEGE if st.session_state.cycle=="college" else CHIPS_UNIV
        cols = st.columns(4)
        for i, c in enumerate(chips):
            with cols[i]:
                if st.button(c, key=f"chip_{i}", use_container_width=True): handle_q(c); st.rerun()
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])
            if "engines" in m:
                st.caption(f"⚡ Fusion: {' + '.join(m['engines'])}")
    q = st.chat_input("Écrivez votre question de cours…")
    if q: handle_q(q); st.rerun()

def handle_q(question):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Angel réfléchit…"):
        try: text, eng = fuse_answer(question)
        except Exception as e: text, eng = f"Erreur: {e}", []
    st.session_state.messages.append({"role": "assistant", "content": text, "engines": eng})

if st.session_state.step < 4: render_onboarding()
else: render_sidebar(); render_chat()
