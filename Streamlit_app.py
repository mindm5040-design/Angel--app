import streamlit as st, requests, base64

st.set_page_config(page_title="LYRA", page_icon="✨", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');
* {font-family:'Inter', sans-serif;}
.stApp {background:#0f0f10; color:#ececec;}
section[data-testid="stSidebar"] {background:#18181b; border-right:1px solid #27272a;}
div[data-testid="stChatMessages"] {gap: 1.6rem!important; padding-top: 2rem; padding-bottom: 4rem;}
.stChatMessage {
    background:#18181b!important;
    border:1px solid #27272a!important;
    border-radius:20px!important;
    padding: 24px 28px!important;
    max-width: 820px!important;
    margin: 0 auto!important;
}
.stChatMessage p,.stChatMessage li {
    font-family:'Source Serif 4', serif!important;
    font-size: 17px!important;
    line-height: 1.85!important;
    letter-spacing: 0.2px!important;
    color: #f4f4f5!important;
}
.stChatMessage h1,.stChatMessage h2,.stChatMessage h3 {
    font-family:'Inter', sans-serif!important;
    font-weight:600!important;
    color:#fff!important;
    margin-top: 1.2em!important;
}
div[data-testid="stChatInput"] {
    background:#18181b!important;
    border:1px solid #3f3f46!important;
    border-radius:24px!important;
    max-width: 820px!important;
    margin: 0 auto!important;
}
.lyra-warning {
    background:#2a1f0f; border:1px solid #92620a; border-radius:12px;
    padding:12px 16px; color:#facc82; font-size:14px; margin-bottom:1rem;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "niveau" not in st.session_state: st.session_state.niveau = "Terminale"
if "cycle" not in st.session_state: st.session_state.cycle = "Lycée"

KEY = st.secrets.get("GROQ_API_KEY", "").strip()
CYCLES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
}
PROGRAMMES = {
    "6e": "bases fractions, décimaux, géométrie simple", "5e": "fractions, proportionnalité", "4e": "Pythagore, Thalès, équations",
    "3e": "fonctions, racine carrée, Brevet", "Seconde": "fonctions, vecteurs", "Première": "dérivées, suites",
    "Terminale": "limites, intégrales, Bac", "Licence 1": "analyse réelle, algèbre linéaire", "Licence 2": "analyse avancée",
    "Licence 3": "topologie", "Master 1": "master recherche", "Master 2": "expert", "Doctorat": "recherche doctorale"
}

# --- Critères de bonne IA pédagogique, intégrés au prompt système ---
# 1. Pédagogie active : guider par indices avant de donner la réponse finale
# 2. Honnêteté : reconnaître l'incertitude plutôt qu'inventer
# 3. Rigueur : vérifier les calculs avant de les présenter comme sûrs
# 4. Portée limitée : rester strictement scolaire, refuser poliment le hors-sujet
# 5. Ton respectueux : encourageant sans flatterie excessive, direct et clair
def system_prompt(niveau, cycle):
    prog = PROGRAMMES.get(niveau, "")
    return f"""Tu es LYRA, tutrice pédagogique d'élite pour le niveau {cycle} {niveau}.
Programme de référence : {prog}.

RÈGLES DE FOND (à respecter strictement) :
1. Reste STRICTEMENT dans le programme de {niveau}. Si la question sort du programme, dis-le poliment et propose une reformulation adaptée au niveau.
2. Ne donne jamais une réponse finale brute sans explication : décompose le raisonnement étape par étape.
3. Quand c'est pertinent, privilégie d'abord un indice ou une question qui aide l'élève à trouver seul, avant de donner la solution complète si l'élève insiste ou bloque.
4. Si tu n'es pas certaine d'un résultat ou d'un calcul, dis-le explicitement plutôt que d'affirmer avec assurance une chose fausse.
5. Vérifie mentalement tes calculs avant de les présenter.
6. Ne fais jamais le travail à la place de l'élève sans qu'il ait au moins tenté de comprendre la méthode.
7. Ton direct, clair, sans flatterie inutile, mais encourageant et respectueux.

Réponse en français clair, aérée, avec titres et exemples adaptés au niveau {niveau}."""

def call_text(q, niveau, cycle):
    if not KEY:
        return "⚠️ Clé API manquante. Configure GROQ_API_KEY dans les secrets Streamlit."
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": system_prompt(niveau, cycle)},
                    {"role": "user", "content": q}
                ]
            },
            timeout=40
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏱️ LYRA met trop de temps à répondre. Réessaie dans un instant."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Problème de connexion avec LYRA : {e}"
    except (KeyError, ValueError):
        return "⚠️ Réponse inattendue reçue. Réessaie ta question."

def call_vision(q, img_bytes, niveau):
    if not KEY:
        return "⚠️ Clé API manquante. Configure GROQ_API_KEY dans les secrets Streamlit."
    try:
        b64 = base64.b64encode(img_bytes).decode()
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {"role": "system", "content": f"Tu es LYRA, tutrice {niveau}. Analyse l'image avec rigueur, décompose le raisonnement étape par étape, et signale si l'écriture ou l'énoncé est ambigu plutôt que de deviner."},
                    {"role": "user", "content": [
                        {"type": "text", "text": q},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}
                ]
            },
            timeout=60
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"⚠️ Problème de connexion avec LYRA : {e}"
    except (KeyError, ValueError):
        return "⚠️ Impossible d'analyser cette image. Réessaie avec une photo plus nette."

def transcribe(b):
    if not KEY:
        return ""
    try:
        files = {"file": ("a.wav", b, "audio/wav")}
        data = {"model": "whisper-large-v3", "language": "fr"}
        r = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {KEY}"},
            files=files, data=data, timeout=60
        )
        r.raise_for_status()
        return r.json().get("text", "")
    except requests.exceptions.RequestException:
        return ""

with st.sidebar:
    st.markdown("## ✨ LYRA")
    if not KEY:
        st.markdown('<div class="lyra-warning">Clé GROQ_API_KEY absente des secrets.</div>', unsafe_allow_html=True)
    cycle = st.segmented_control("Cycle", list(CYCLES.keys()), default=st.session_state.cycle)
    if cycle: st.session_state.cycle = cycle
    niveau = st.segmented_control("Niveau", CYCLES[st.session_state.cycle], default=st.session_state.niveau if st.session_state.niveau in CYCLES[st.session_state.cycle] else CYCLES[st.session_state.cycle][0])
    if niveau: st.session_state.niveau = niveau
    st.markdown("---")
    st.caption(f"🔒 Verrouillé sur {st.session_state.niveau}")
    st.file_uploader("📸 Photo exo", type=["jpg", "png", "jpeg"], key="up")
    st.camera_input("Caméra", key="cam", label_visibility="collapsed")
    st.audio_input("🎙️ Vocal", key="aud", label_visibility="collapsed")
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown(f"### ✨ LYRA • {st.session_state.cycle} — {st.session_state.niveau}")
st.caption("Ta tutrice pédagogique : elle t'aide à comprendre, pas seulement à trouver la réponse")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Photo
img = st.session_state.get("cam") or st.session_state.get("up")
if img and (st.session_state.get("up") is not None or st.session_state.get("cam") is not None):
    if st.button("📸 Analyser la photo"):
        ans = call_vision("Résous l'exercice sur l'image étape par étape", img.getvalue(), st.session_state.niveau)
        st.session_state.messages.append({"role": "user", "content": "📸 [Photo d'exercice]"})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

# Vocal
aud = st.session_state.get("aud")
if aud:
    txt = transcribe(aud.getvalue())
    if txt:
        st.session_state.messages.append({"role": "user", "content": f"🎙️ {txt}"})
        ans = call_text(txt, st.session_state.niveau, st.session_state.cycle)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
    else:
        st.warning("Je n'ai pas réussi à comprendre l'audio, réessaie ou écris ta question.")

q = st.chat_input(f"Question de {st.session_state.niveau}...")
if q:
    st.session_state.messages.append({"role": "user", "content": q})
    ans = call_text(q, st.session_state.niveau, st.session_state.cycle)
    st.session_state.messages.append({"role": "assistant", "content": ans})
    st.rerun()
