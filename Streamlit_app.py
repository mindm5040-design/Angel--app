import streamlit as st
import requests
import base64
import time
import re
import json
import uuid

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

st.markdown("""
<style>
#MainMenu, footer, header {
    visibility: hidden;
}

.stApp {
    background: #212121;
    color: #ececec;
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid #2f2f2f !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0.7rem 0.65rem 0.8rem 0.65rem;
}

.lyra-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px 18px 10px;
}

.lyra-logo {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    color: white;
    font-size: 17px;
    box-shadow: 0 4px 18px rgba(99,102,241,.25);
}

.lyra-brand-name {
    color: #f5f5f5;
    font-weight: 650;
    font-size: 16px;
}

.lyra-brand-sub {
    color: #8e8e8e;
    font-size: 10px;
    margin-top: 1px;
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
    color: #fff !important;
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

/* TOPBAR */

.lyra-topbar {
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(33,33,33,.92);
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

/* CHAT */

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

div[data-testid="stChatMessage"] pre {
    border-radius: 10px !important;
    border: 1px solid #3a3a3a !important;
}

/* WELCOME */

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
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 28px;
    margin-bottom: 22px;
    box-shadow: 0 10px 35px rgba(99,102,241,.25);
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

/* CHAT INPUT */

div[data-testid="stChatInput"] {
    max-width: 820px !important;
    margin: 0 auto !important;
    background: #2f2f2f !important;
    border: 1px solid #444 !important;
    border-radius: 26px !important;
}

div[data-testid="stChatInput"] textarea {
    color: #f5f5f5 !important;
    background: transparent !important;
}

/* WARNINGS */

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

/* FOOTER */

.lyra-footer {
    text-align: center;
    color: #777;
    font-size: 11px;
    padding: 12px 0 22px;
}

/* MOBILE */

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
""", unsafe_allow_html=True)


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


# ============================================================
# DONNÉES
# ============================================================

KEY = st.secrets.get("GROQ_API_KEY", "").strip()


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
    ],
}


PROGRAMMES = {

    "6e":
        "fractions, décimaux, géométrie simple",

    "5e":
        "fractions, proportionnalité",

    "4e":
        "Pythagore, Thalès, équations",

    "3e":
        "fonctions, racine carrée, Brevet",

    "Seconde":
        "fonctions, vecteurs",

    "Première":
        "dérivées, suites",

    "Terminale":
        "limites, intégrales, Bac",

    "Licence 1":
        "analyse réelle, algèbre linéaire",

    "Licence 2":
        "analyse avancée",

    "Licence 3":
        "topologie",

    "Master 1":
        "recherche avancée",

    "Master 2":
        "expert",

    "Doctorat":
        "recherche doctorale",
}


MINEUR_CYCLES = {
    "Collège",
    "Lycée"
}


# ============================================================
# SÉCURITÉ
# ============================================================

CRISIS_PATTERNS = [

    r"\bsuicid",
    r"\bme tuer\b",
    r"\bme faire du mal\b",
    r"\benvie de mourir\b",
    r"\bscarification",
    r"\bplus envie de vivre\b",
    r"\bharc[eè]l"

]


def detect_crisis(text: str) -> bool:

    text = text.lower()

    return any(
        re.search(pattern, text)
        for pattern in CRISIS_PATTERNS
    )


CRISIS_MESSAGE = """
Ce que tu traverses semble difficile, et ça compte.

Je suis une IA pédagogique et je ne suis pas la bonne ressource
pour gérer une situation de crise.

Le plus important est de contacter une personne réelle capable
de t'aider immédiatement.

Si tu es en danger immédiat, contacte les services d'urgence
de ton pays ou demande directement de l'aide à un adulte de confiance.

Tu n'as pas à gérer ça seul(e).
"""


# ============================================================
# CONVERSATIONS
# ============================================================

def current_messages():

    return st.session_state.conversations[
        st.session_state.current_conv
    ]["messages"]


def set_conv_title_from_first_message(text):

    conv = st.session_state.conversations[
        st.session_state.current_conv
    ]

    if conv["title"] == "Nouvelle conversation":

        clean = text.strip().replace("\n", " ")

        conv["title"] = (
            clean[:42] +
            ("…" if len(clean) > 42 else "")
        )


def new_conversation():

    new_id = str(uuid.uuid4())

    st.session_state.conversations[new_id] = {
        "title": "Nouvelle conversation",
        "messages": []
    }

    st.session_state.current_conv = new_id


# ============================================================
# PROMPT
# ============================================================

def system_prompt(niveau, cycle):

    prog = PROGRAMMES.get(niveau, "")

    contexte_mineur = ""

    if cycle in MINEUR_CYCLES:

        contexte_mineur = """
L'élève est probablement mineur.

Garde les réponses adaptées à son âge.

Ne développe pas de contenu sexuel,
violent ou lié aux substances.
"""


    return f"""
Tu es LYRA, une assistante pédagogique polyvalente.

L'élève est en {cycle}, niveau {niveau}.

Programme de référence :
{prog}

RÈGLES :

1. Tu es avant tout une tutrice pédagogique.

2. Pour les exercices scolaires,
explique le raisonnement étape par étape.

3. Ne donne pas uniquement le résultat final.

4. Si l'élève apprend,
privilégie les indices et les exemples.

5. Vérifie les calculs avant de répondre.

6. Si tu n'es pas sûre,
indique ton incertitude.

7. Ne prétends jamais être humaine.

8. Reste chaleureuse sans créer
de dépendance affective.

9. Pour les sujets politiques,
religieux ou sociétaux,
reste neutre.

10. Refuse les demandes dangereuses
ou illégales.

11. Ne prétends jamais avoir accès
à une information que tu n'as pas.

{contexte_mineur}

Réponds en français clair et naturel.

Utilise Markdown lorsque cela améliore
la compréhension.
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


        if content.startswith("📸 [Photo"):

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
            +
            extra_context[:8000]
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
        now -
        st.session_state.last_call
        <
        MIN_INTERVAL
    ):

        return False


    st.session_state.last_call = now

    return True


# ============================================================
# TEXTE GROQ
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
            "Ajoute `GROQ_API_KEY` "
            "dans les secrets Streamlit."
        )

        return


    if not cooldown_ok():

        yield (
            "⏳ Attends un instant "
            "avant d'envoyer "
            "une nouvelle question."
        )

        return


    response = None


    try:

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
                    "openai/gpt-oss-20b",

                "messages":
                    build_messages(
                        question,
                        niveau,
                        cycle,
                        extra_context
                    ),

                "temperature":
                    0.5,

                "stream":
                    True

            },

            timeout=60,

            stream=True

        )


        if not response.ok:

            detail = response.text[:500]

            yield (
                f"⚠️ Erreur API Groq "
                f"({response.status_code}) : "
                f"{detail}"
            )

            return


        for line in response.iter_lines(
            decode_unicode=True
        ):

            if not line:
                continue


            if not line.startswith("data: "):
                continue


            payload = line[6:].strip()


            if payload == "[DONE]":
                break


            try:

                chunk = json.loads(
                    payload
                )


                delta = (

                    chunk
                    .get(
                        "choices",
                        [{}]
                    )[0]
                    .get(
                        "delta",
                        {}
                    )
                    .get(
                        "content",
                        ""
                    )

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
            "⏱️ LYRA met trop de temps "
            "à répondre. Réessaie."
        )


    except requests.exceptions.RequestException as error:

        yield (
            "⚠️ Problème de connexion "
            f"avec LYRA : "
            f"{type(error).__name__}"
        )


    finally:

        if response is not None:
            response.close()


# ============================================================
# VISION
# ============================================================

def call_vision(
    question,
    image_bytes,
    niveau,
    mime_type="image/jpeg"
):

    if not KEY:

        return (
            "⚠️ Clé API manquante. "
            "Configure `GROQ_API_KEY`."
        )


    if not cooldown_ok():

        return (
            "⏳ Attends un instant "
            "avant d'envoyer "
            "une nouvelle demande."
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
                    "qwen/qwen3.6-27b",

                "messages": [

                    {

                        "role":
                            "system",

                        "content":
                            f"""
Tu es LYRA, tutrice pédagogique
pour un élève de {niveau}.

Analyse uniquement l'exercice scolaire
présent dans l'image.

Lis attentivement les nombres,
symboles et consignes.

Si quelque chose est illisible,
dis-le au lieu d'inventer.

Explique le raisonnement étape par étape.
"""

                    },

                    {

                        "role":
                            "user",

                        "content": [

                            {

                                "type":
                                    "text",

                                "text":
                                    question or
                                    "Analyse cet exercice."

                            },

                            {

                                "type":
                                    "image_url",

                                "image_url": {

                                    "url":
                                        (
                                            f"data:"
                                            f"{mime_type};base64,"
                                            f"{encoded}"
                                        )

                                }

                            }

                        ]

                    }

                ],

                "temperature":
                    0.3,

                "max_completion_tokens":
                    2048

            },

            timeout=60

        )


        if not response.ok:

            return (
                f"⚠️ Erreur vision "
                f"({response.status_code}) : "
                f"{response.text[:500]}"
            )


        data = response.json()


        return (
            data["choices"][0]
            ["message"]
            ["content"]
        )


    except requests.exceptions.RequestException as error:

        return (
            "⚠️ Problème de connexion : "
            f"{type(error).__name__}"
        )


    except (
        KeyError,
        ValueError,
        IndexError,
        TypeError
    ):

        return (
            "⚠️ Impossible d'analyser "
            "cette image. "
            "Essaie avec une photo plus nette."
        )


# ============================================================
# TRANSCRIPTION AUDIO
# ============================================================

def transcribe(
    audio_bytes,
    filename="audio.wav",
    mime_type="audio/wav"
):

    if not KEY:
        return ""


    try:

        response = requests.post(

            "https://api.groq.com/openai/v1/audio/transcriptions",

            headers={

                "Authorization":
                    f"Bearer {KEY}"

            },

            files={

                "file": (

                    filename,
                    audio_bytes,
                    mime_type

                )

            },

            data={

                "model":
                    "whisper-large-v3-turbo",

                "response_format":
                    "json"

            },

            timeout=60

        )


        if not response.ok:
            return ""


        data = response.json()


        return data.get(
            "text",
            ""
        ).strip()


    except (
        requests.exceptions.RequestException,
        ValueError,
        TypeError
    ):

        return ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        
