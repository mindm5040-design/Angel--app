import streamlit as st
import requests
import base64
import time
import re
import json
import uuid
import io
import hashlib


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LYRA",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

#MainMenu,
footer,
header {
    visibility: hidden;
}

.stApp {
    background: #212121;
    color: #ececec;
}

html,
body,
[class*="css"] {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


/* ============================================================
   SIDEBAR
============================================================ */

section[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid #2f2f2f !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0.7rem 0.65rem;
}

.lyra-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px 18px;
}

.lyra-logo {
    width: 34px;
    height: 34px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #6366f1
    );
    color: white;
    font-size: 18px;
    box-shadow:
        0 4px 18px rgba(99, 102, 241, .25);
}

.lyra-brand-name {
    color: #f5f5f5;
    font-weight: 650;
    font-size: 17px;
}

.lyra-brand-sub {
    color: #8e8e8e;
    font-size: 10px;
    margin-top: 2px;
}

section[data-testid="stSidebar"] button {
    border-radius: 9px !important;
    border: 0 !important;
    background: transparent !important;
    color: #d4d4d4 !important;
}

section[data-testid="stSidebar"] button:hover {
    background: #2a2a2a !important;
    color: white !important;
}

.new-chat-btn button {
    background: #2a2a2a !important;
    border: 1px solid #3b3b3b !important;
    color: white !important;
    height: 42px !important;
}

.conv-btn button {
    text-align: left !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    font-size: 13px !important;
    padding: 8px 10px !important;
}

.sidebar-section {
    color: #8e8e8e;
    font-size: 11px;
    font-weight: 600;
    padding: 16px 10px 6px;
}

.sidebar-bottom {
    border-top: 1px solid #303030;
    margin-top: 16px;
    padding-top: 12px;
}


/* ============================================================
   TOP BAR
============================================================ */

.lyra-topbar {
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(33, 33, 33, .92);
    backdrop-filter: blur(12px);
}

.lyra-model {
    font-size: 16px;
    font-weight: 600;
    color: #ececec;
}

.lyra-model span {
    color: #9b9b9b;
    font-weight: 400;
}


/* ============================================================
   CHAT
============================================================ */

div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 20px 0 !important;
    margin: 0 auto !important;
    max-width: 820px !important;
}

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li {
    font-size: var(--lyra-font-size, 15.5px) !important;
    line-height: 1.75 !important;
    color: #ececec !important;
}

div[data-testid="stChatMessage"] code {
    font-family:
        "SFMono-Regular",
        Consolas,
        monospace !important;
}

div[data-testid="stChatMessage"] pre {
    border-radius: 10px !important;
    border: 1px solid #3a3a3a !important;
}


/* ============================================================
   WELCOME
============================================================ */

.lyra-welcome {
    min-height: 55vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 50px 20px;
}

.lyra-welcome-logo {
    width: 60px;
    height: 60px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #6366f1
    );
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 29px;
    margin-bottom: 22px;
    box-shadow:
        0 10px 35px rgba(99, 102, 241, .25);
}

.lyra-welcome h1 {
    font-size: 29px;
    color: #f5f5f5;
    margin: 0 0 8px;
    font-weight: 600;
}

.lyra-welcome p {
    color: #9b9b9b;
    font-size: 14px;
    margin: 0;
}


/* ============================================================
   CHAT INPUT
============================================================ */

div[data-testid="stChatInput"] {
    max-width: 820px !important;
    margin: 0 auto !important;
    background: #2f2f2f !important;
    border: 1px solid #444 !important;
    border-radius: 26px !important;
    box-shadow:
        0 5px 30px rgba(0, 0, 0, .20) !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: #5c5c5c !important;
}

div[data-testid="stChatInput"] textarea {
    color: #f5f5f5 !important;
    background: transparent !important;
    font-size: 15px !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #9a9a9a !important;
}


/* ============================================================
   PANELS
============================================================ */

.lyra-warning {
    background: #2d2414;
    border: 1px solid #6b531d;
    border-radius: 10px;
    padding: 11px 13px;
    color: #f5d48a;
    font-size: 12px;
    margin-bottom: 12px;
}

.lyra-crisis {
    background: #321919;
    border: 1px solid #713333;
    border-radius: 12px;
    padding: 15px;
    color: #fecaca;
    font-size: 14px;
    line-height: 1.6;
}

.tool-label {
    color: #aaa;
    font-size: 12px;
    margin: 7px 3px 4px;
}


/* ============================================================
   FOOTER
============================================================ */

.lyra-footer {
    text-align: center;
    color: #777;
    font-size: 11px;
    padding: 12px 0 22px;
}


/* ============================================================
   MOBILE
============================================================ */

@media (max-width: 768px) {

    section[data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
    }

    div[data-testid="stChatMessage"] {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }

    div[data-testid="stChatInput"] {
        max-width: calc(100% - 16px) !important;
    }

    .lyra-welcome h1 {
        font-size: 24px;
    }

    .lyra-topbar {
        padding: 0 10px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "conversations" not in st.session_state:

    first_id = str(uuid.uuid4())

    st.session_state.conversations = {
        first_id: {
            "title": "Nouvelle conversation",
            "messages": []
        }
    }

    st.session_state.current_conv = first_id


if "niveau" not in st.session_state:
    st.session_state.niveau = "Terminale"


if "cycle" not in st.session_state:
    st.session_state.cycle = "Lycée"


if "last_call" not in st.session_state:
    st.session_state.last_call = 0.0


if "font_size" not in st.session_state:
    st.session_state.font_size = "Normale"


if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = ""


if "processed_image" not in st.session_state:
    st.session_state.processed_image = ""


# ============================================================
# API KEY
# ============================================================

try:
    KEY = st.secrets.get("GROQ_API_KEY", "").strip()
except Exception:
    KEY = ""


# ============================================================
# MODÈLES GROQ
# ============================================================

TEXT_MODEL = "openai/gpt-oss-20b"

VISION_MODEL = (
    "meta-llama/"
    "llama-4-scout-17b-16e-instruct"
)

AUDIO_MODEL = "whisper-large-v3-turbo"


# ============================================================
# DONNÉES PÉDAGOGIQUES
# ============================================================

CYCLES = {

    "Collège": [
        "6e",
        "5e",
        "4e",
        "3e"
    ],

    "Lycée": [
        "Seconde",
        "Première",
        "Terminale"
    ],

    "Université": [
        "Licence 1",
        "Licence 2",
        "Licence 3",
        "Master 1",
        "Master 2",
        "Doctorat"
    ]
}


PROGRAMMES = {

    "6e":
        "fractions, décimaux, géométrie, calcul",

    "5e":
        "fractions, proportionnalité, géométrie",

    "4e":
        "Pythagore, Thalès, équations, calcul",

    "3e":
        "fonctions, racines carrées, équations, Brevet",

    "Seconde":
        "fonctions, vecteurs, équations, statistiques",

    "Première":
        "dérivées, suites, probabilités, fonctions",

    "Terminale":
        "limites, dérivées, intégrales, probabilités, Bac",

    "Licence 1":
        "analyse, algèbre linéaire, probabilités",

    "Licence 2":
        "analyse avancée, algèbre, statistiques",

    "Licence 3":
        "topologie, analyse, algèbre avancée",

    "Master 1":
        "mathématiques avancées, recherche",

    "Master 2":
        "mathématiques avancées, recherche",

    "Doctorat":
        "recherche scientifique et raisonnement avancé"
}


MINEUR_CYCLES = {
    "Collège",
    "Lycée"
}


# ============================================================
# CONVERSATIONS
# ============================================================

def current_messages():

    return st.session_state.conversations[
        st.session_state.current_conv
    ]["messages"]


def set_conv_title_from_first_message(text):

    conversation = st.session_state.conversations[
        st.session_state.current_conv
    ]

    if conversation["title"] == "Nouvelle conversation":

        clean = (
            text
            .strip()
            .replace("\n", " ")
        )

        if len(clean) > 42:
            clean = clean[:42] + "…"

        conversation["title"] = clean


def new_conversation():

    new_id = str(uuid.uuid4())

    st.session_state.conversations[new_id] = {
        "title": "Nouvelle conversation",
        "messages": []
    }

    st.session_state.current_conv = new_id


# ============================================================
# SÉCURITÉ
# ============================================================

CRISIS_PATTERNS = [

    r"\bsuicid",

    r"\bme tuer\b",

    r"\bme faire du mal\b",

    r"\benvie de mourir\b",

    r"\bscarification",

    r"\bplus envie de vivre\b"
]


def detect_crisis(text):

    text = text.lower()

    return any(
        re.search(pattern, text)
        for pattern in CRISIS_PATTERNS
    )


CRISIS_MESSAGE = """
Ce que tu traverses semble difficile, et ça compte.

Je suis une IA pédagogique et je ne suis pas la bonne
ressource pour gérer une situation de crise.

Le plus important est de contacter une personne réelle
capable de t'aider immédiatement.

Si tu es en danger immédiat, contacte les services
d'urgence de ton pays ou demande directement de l'aide
à une personne de confiance.

Tu n'as pas à gérer ça seul(e).
"""


PRIVACY_NOTE = (
    "L'historique est conservé dans la session Streamlit. "
    "Les messages envoyés à LYRA sont transmis à Groq "
    "pour générer les réponses."
)


# ============================================================
# PROMPT SYSTÈME
# ============================================================

def system_prompt(niveau, cycle):

    programme = PROGRAMMES.get(
        niveau,
        ""
    )

    mineur_context = ""

    if cycle in MINEUR_CYCLES:

        mineur_context = """
L'élève est probablement mineur.
Adapte ton langage à son âge.
Évite tout contenu sexuel explicite,
violent ou lié aux substances.
"""


    return f"""
Tu es LYRA, une assistante pédagogique polyvalente.

L'élève est en {cycle}, niveau {niveau}.

Programme de référence :
{programme}

OBJECTIF :

Aider l'élève à comprendre et progresser,
pas simplement lui donner des réponses.

RÈGLES :

1. Explique clairement les raisonnements.

2. Pour les exercices, donne les étapes.

3. Ne donne pas uniquement le résultat final.

4. Utilise des exemples simples lorsque nécessaire.

5. Vérifie tes calculs avant de répondre.

6. Si une information est incertaine,
   indique-le clairement.

7. Ne prétends jamais être humaine.

8. Ne crée pas de dépendance affective.

9. Reste respectueuse et pédagogique.

10. Pour les sujets sensibles ou controversés,
    reste neutre et factuelle.

11. Refuse les demandes dangereuses ou illégales.

12. Ne prétends jamais avoir accès à une information
    que tu n'as pas.

13. Réponds en français sauf si l'élève demande
    explicitement une autre langue.

14. Utilise Markdown lorsque cela améliore
    la compréhension.

{mineur_context}
"""


# ============================================================
# HISTORIQUE
# ============================================================

def build_messages(
    user_question,
    niveau,
    cycle,
    extra_context=""
):

    messages = [

        {
            "role": "system",
            "content": system_prompt(
                niveau,
                cycle
            )
        }

    ]

    history = current_messages()[-12:]

    for message in history:

        role = message.get("role")

        if role not in {
            "user",
            "assistant"
        }:
            continue

        content = message.get(
            "content",
            ""
        )

        if content.startswith(
            "📸 [Photo d'exercice]"
        ):

            content = (
                "L'utilisateur a envoyé "
                "une photo d'exercice."
            )

        messages.append({

            "role": role,

            "content": content

        })


    user_content = user_question

    if extra_context:

        user_content += (
            "\n\n"
            "[Contexte du document joint]\n"
            + extra_context[:12000]
        )


    messages.append({

        "role": "user",

        "content": user_content

    })


    return messages


# ============================================================
# COOLDOWN
# ============================================================

MIN_INTERVAL = 1.5


def cooldown_ok():

    now = time.time()

    if (
        now
        - st.session_state.last_call
        < MIN_INTERVAL
    ):

        return False

    st.session_state.last_call = now

    return True


# ============================================================
# STREAMING TEXTE
# ============================================================

def stream_text(
    question,
    niveau,
    cycle,
    extra_context=""
):

    if not KEY:

        yield (
            "⚠️ **Clé API manquante.**\n\n"
            "Ajoute `GROQ_API_KEY` dans les "
            "Secrets de ton application Streamlit."
        )

        return


    if not cooldown_ok():

        yield (
            "⏳ Attends un instant avant "
            "d'envoyer une nouvelle question."
        )

        return


    messages = build_messages(
        question,
        niveau,
        cycle,
        extra_context
    )


    try:

        with requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers={

                "Authorization":
                    f"Bearer {KEY}",

                "Content-Type":
                    "application/json"
            },

            json={

                "model":
                    TEXT_MODEL,

                "messages":
                    messages,

                "temperature":
                    0.5,

                "max_completion_tokens":
                    4096,

                "stream":
                    True
            },

            timeout=90,

            stream=True

        ) as response:


            if not response.ok:

                try:

                    error_data = response.json()

                    error_message = (
                        error_data
                        .get("error", {})
                        .get("message")
                    )

                except Exception:

                    error_message = None


                if error_message:

                    yield (
                        "⚠️ **Erreur Groq :**\n\n"
                        + str(error_message)
                    )

                else:

                    yield (
                        "⚠️ **Erreur API Groq :** "
                        f"HTTP {response.status_code}"
                    )

                return


            for line in response.iter_lines():

                if not line:
                    continue


                if isinstance(
                    line,
                    bytes
                ):

                    line = line.decode(
                        "utf-8"
                    )


                if not line.startswith(
                    "data: "
                ):

                    continue


                payload = line[6:]


                if payload.strip() == "[DONE]":
                    break


                try:

                    chunk = json.loads(
                        payload
                    )


                    choices = chunk.get(
                        "choices",
                        []
                    )

                    if not choices:
                        continue


                    delta = (
                        choices[0]
                        .get("delta", {})
                        .get("content", "")
                    )


                    if delta:
                        yield delta


                except (
                    json.JSONDecodeError,
                    KeyError,
                    IndexError,
                    TypeError
                ):

                    continue


    except requests.exceptions.Timeout:

        yield (
            "⏱️ LYRA met trop de temps à répondre. "
            "Réessaie dans un instant."
        )


    except requests.exceptions.RequestException as error:

        yield (
            "⚠️ Problème de connexion avec Groq : "
            f"{type(error).__name__}"
        )


# ============================================================
# VISION
# ============================================================

def call_vision(
    question,
    image_bytes,
    niveau
):

    if not KEY:

        return (
            "⚠️ Clé API manquante. "
            "Configure `GROQ_API_KEY`."
        )


    if not cooldown_ok():

        return (
            "⏳ Attends un instant avant "
            "d'envoyer une nouvelle demande."
        )


    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode("utf-8")


        response = requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers={

                "Authorization":
                    f"Bearer {KEY}",

                "Content-Type":
                    "application/json"
            },

            json={

                "model":
                    VISION_MODEL,

                "temperature":
                    0.2,

                "max_completion_tokens":
                    4096,

                "messages": [

                 
