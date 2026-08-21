import streamlit as st, requests, base64, time, re, json, uuid
# FIX PWA BUILDER - Ajoute un vrai manifest pour Lyra
manifest_code = """
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiTHlyYSBBSSIsInNob3J0X25hbWUiOiJMeXJhIiwiZGlzcGxheSI6InN0YW5kYWxvbmUiLCJiYWNrZ3JvdW5kX2NvbG9yIjoiI0ZDRENFOSIsInRoZW1lX2NvbG9yIjoiI0UwN0E0RiIsImljb25zIjpbXX0=">
<link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/4712/4712027.png">
<meta name="theme-color" content="#E07A4F">
"""
st.markdown(manifest_code, unsafe_allow_html=True)
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
    font-size: var(--lyra-font-size, 17px)!important;
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
.lyra-crisis {
    background:#2a0f0f; border:1px solid #b91c1c; border-radius:12px;
    padding:14px 18px; color:#fecaca; font-size:14px; margin-bottom:1rem; line-height:1.6;
}
.lyra-footer {
    text-align:center; color:#71717a; font-size:12px; padding:1.5rem 0 0.5rem 0;
}
.conv-btn button {
    text-align:left!important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CRITÈRES D'UNE BONNE IA — appliqués dans tout le fichier
# 1. Utilité & pédagogie active     6. Sécurité des mineurs & contenu approprié
# 2. Honnêteté & transparence       7. Anti-dépendance affective
# 3. Sécurité & gestion de crise    8. Robustesse technique & accessibilité
# 4. Confidentialité & sobriété     9. Limites clairement énoncées
#    des données                   10. Expérience type ChatGPT (historique de
# 5. Neutralité & absence de biais      conversations, réponse en flux, fichiers)
# ---------------------------------------------------------------------------

# --- 10. Multi-conversations façon ChatGPT ---------------------------------
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {first_id: {"title": "Nouvelle conversation", "messages": []}}
    st.session_state.current_conv = first_id
if "niveau" not in st.session_state: st.session_state.niveau = "Terminale"
if "cycle" not in st.session_state: st.session_state.cycle = "Lycée"
if "last_call" not in st.session_state: st.session_state.last_call = 0.0
if "font_size" not in st.session_state: st.session_state.font_size = "Normale"

def current_messages():
    return st.session_state.conversations[st.session_state.current_conv]["messages"]

def set_conv_title_from_first_message(text):
    conv = st.session_state.conversations[st.session_state.current_conv]
    if conv["title"] == "Nouvelle conversation":
        conv["title"] = (text[:40] + "…") if len(text) > 40 else text

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
MINEUR_CYCLES = {"Collège", "Lycée"}  # utilisateurs probablement mineurs -> ton et contenu adaptés

# --- 3. Sécurité & gestion de crise -----------------------------------------
CRISIS_PATTERNS = [
    r"\bsuicid", r"\bme tuer\b", r"\bme faire du mal\b", r"\benvie de mourir\b",
    r"\bscarification", r"\bplus envie de vivre\b", r"\bharc[eè]l"
]

def detect_crisis(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in CRISIS_PATTERNS)

CRISIS_MESSAGE = """Ce que tu traverses semble difficile, et ça compte. Je suis une IA pédagogique et je ne suis pas la bonne ressource pour ça — mais il existe des personnes formées pour t'aider vraiment.

**En France :**
- **3114** — numéro national de prévention du suicide, gratuit, 24h/24
- **Fil Santé Jeunes : 0 800 235 236** (appel et tchat anonymes)
- Ou parle à un adulte de confiance : parent, infirmier(ère) scolaire, professeur

Tu n'as pas à traverser ça seul(e). N'hésite pas à contacter une de ces ressources."""

PRIVACY_NOTE = "LYRA ne conserve tes conversations que dans ton navigateur pour cette session — rien n'est envoyé à un serveur permanent par l'application elle-même."

# --- 1, 2, 5, 6, 7, 10. Prompt système --------------------------------------
# Comportement assoupli façon ChatGPT : LYRA répond volontiers à des questions
# hors programme (curiosité générale, culture, aide méthodologique...) au lieu
# de les refuser, tout en restant identifiable comme tutrice scolaire et en
# recentrant naturellement vers le niveau de l'élève quand c'est pertinent.
def system_prompt(niveau, cycle):
    prog = PROGRAMMES.get(niveau, "")
    contexte_mineur = ""
    if cycle in MINEUR_CYCLES:
        contexte_mineur = """
9. L'élève est probablement mineur : garde un contenu strictement adapté à son âge, sans aucune ambiguïté, et ne développe jamais de sujets sensibles (violence, sexualité, substances) même si la question dévie vers ça — recentre poliment sur le scolaire."""
    return f"""Tu es LYRA, assistante pédagogique polyvalente pour un élève de {cycle} {niveau}.
Programme de référence pour ce niveau : {prog}.

RÈGLES DE FOND (à respecter strictement) :
1. Tu es avant tout une tutrice scolaire pour {niveau}, mais comme un assistant IA généraliste, tu peux répondre à des questions hors programme (culture générale, méthode de travail, curiosité, aide à la rédaction, etc.) au lieu de refuser — adapte simplement le niveau de langage à l'âge de l'élève.
2. Pour les exercices et notions du programme, ne donne jamais une réponse finale brute sans explication : décompose le raisonnement étape par étape, et privilégie un indice avant la solution complète si l'élève bloque.
3. Si tu n'es pas certaine d'un résultat ou d'un calcul, dis-le explicitement plutôt que d'affirmer avec assurance une chose fausse.
4. Vérifie mentalement tes calculs avant de les présenter.
5. Ne fais jamais le travail à la place de l'élève sans qu'il ait au moins tenté de comprendre la méthode, pour les exercices notés/évalués.
6. Reste neutre sur toute question politique, religieuse ou sociétale : présente les faits et différents points de vue, jamais une opinion personnelle.
7. Tu es une IA, pas un ami ni un confident : reste chaleureuse et encourageante, mais rappelle si besoin que tu es un outil, pas un substitut à des relations humaines réelles.
8. Refuse poliment tout contenu dangereux, illégal ou inapproprié, indépendamment du sujet scolaire ou non.{contexte_mineur}

Ton direct, clair, sans flatterie inutile, mais encourageant et respectueux.
Réponse en français clair, aérée, avec titres et exemples adaptés au niveau {niveau}."""

# --- 8. Robustesse technique : cooldown simple anti-abus / anti-surcoût ----
MIN_INTERVAL = 1.5

def cooldown_ok():
    now = time.time()
    if now - st.session_state.last_call < MIN_INTERVAL:
        return False
    st.session_state.last_call = now
    return True

# --- 10. Réponse en flux façon ChatGPT --------------------------------------
def stream_text(q, niveau, cycle, extra_context=""):
    if not KEY:
        yield "⚠️ Clé API manquante. Configure GROQ_API_KEY dans les secrets Streamlit."
        return
    if not cooldown_ok():
        yield "⏳ Une question à la fois — attends une seconde avant d'envoyer la suivante."
        return
    user_content = q if not extra_context else f"{q}\n\n[Contexte du fichier joint]\n{extra_context[:6000]}"
    try:
        with requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": system_prompt(niveau, cycle)},
                    {"role": "user", "content": user_content}
                ],
                "stream": True
            },
            timeout=60,
            stream=True
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if not line.startswith("data: "):
                    continue
                payload = line[len("data: "):]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except (KeyError, IndexError, json.JSONDecodeError):
                    continue
    except requests.exceptions.Timeout:
        yield "⏱️ LYRA met trop de temps à répondre. Réessaie dans un instant."
    except requests.exceptions.RequestException as e:
        yield f"⚠️ Problème de connexion avec LYRA : {type(e).__name__}"

def call_vision(q, img_bytes, niveau):
    if not KEY:
        return "⚠️ Clé API manquante. Configure GROQ_API_KEY dans les secrets Streamlit."
    if not cooldown_ok():
        return "⏳ Une question à la fois — attends une seconde avant d'envoyer la suivante."
    try:
        b64 = base64.b64encode(img_bytes).decode()
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {"role": "system", "content": f"Tu es LYRA, tutrice {niveau}. Analyse l'image avec rigueur, décompose le raisonnement étape par étape, et signale si l'écriture ou l'énoncé est ambigu plutôt que de deviner. Si l'image ne contient pas d'exercice scolaire, dis-le poliment sans analyser le reste du contenu."},
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
        return f"⚠️ Problème de connexion avec LYRA : {type(e).__name__}"
    except (KeyError, ValueError, IndexError):
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

# --- 10. Upload de documents (pdf/txt) façon ChatGPT ------------------------
def extract_document_text(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        try:
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
        except Exception:
            return ""
    if name.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            return "[PyPDF2 non installé : impossible d'extraire ce PDF côté serveur]"
        except Exception:
            return "[Impossible de lire ce PDF]"
    return ""

with st.sidebar:
    st.markdown("## ✨ LYRA")
    if not KEY:
        st.markdown('<div class="lyra-warning">Clé GROQ_API_KEY absente des secrets.</div>', unsafe_allow_html=True)

    if st.button("➕ Nouvelle conversation", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.conversations[new_id] = {"title": "Nouvelle conversation", "messages": []}
        st.session_state.current_conv = new_id
        st.rerun()

    st.caption("Conversations")
    # --- 10. Historique des conversations façon ChatGPT ---
    for conv_id, conv in list(st.session_state.conversations.items()):
        cols = st.columns([5, 1])
        active = conv_id == st.session_state.current_conv
        with cols[0]:
            st.markdown('<div class="conv-btn">', unsafe_allow_html=True)
            if st.button(("🟢 " if active else "") + conv["title"], key=f"sel_{conv_id}", use_container_width=True):
                st.session_state.current_conv = conv_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with cols[1]:
            if len(st.session_state.conversations) > 1 and st.button("🗑️", key=f"del_{conv_id}"):
                del st.session_state.conversations[conv_id]
                if st.session_state.current_conv == conv_id:
                    st.session_state.current_conv = next(iter(st.session_state.conversations))
                st.rerun()

    st.markdown("---")
    cycle = st.segmented_control("Cycle", list(CYCLES.keys()), default=st.session_state.cycle)
    if cycle: st.session_state.cycle = cycle
    niveau = st.segmented_control("Niveau", CYCLES[st.session_state.cycle], default=st.session_state.niveau if st.session_state.niveau in CYCLES[st.session_state.cycle] else CYCLES[st.session_state.cycle][0])
    if niveau: st.session_state.niveau = niveau
    st.caption(f"🔒 Verrouillé sur {st.session_state.niveau}")

    st.markdown("---")
    st.file_uploader("📸 Photo exo", type=["jpg", "png", "jpeg"], key="up")
    st.camera_input("Caméra", key="cam", label_visibility="collapsed")
    st.audio_input("🎙️ Vocal", key="aud", label_visibility="collapsed")
    st.file_uploader("📄 Document (pdf/txt)", type=["pdf", "txt"], key="doc")

    st.markdown("---")
    font_choice = st.select_slider("🔠 Taille du texte", options=["Petite", "Normale", "Grande"], value=st.session_state.font_size)
    st.session_state.font_size = font_choice

    st.markdown("---")
    with st.expander("ℹ️ À propos de LYRA"):
        st.caption("LYRA est une intelligence artificielle, pas un enseignant humain. Elle peut se tromper : vérifie toujours les points importants avec ton professeur.")
        st.caption(PRIVACY_NOTE)

_size_map = {"Petite": "15px", "Normale": "17px", "Grande": "20px"}
st.markdown(f"<style>:root {{ --lyra-font-size: {_size_map[st.session_state.font_size]}; }}</style>", unsafe_allow_html=True)

st.markdown(f"### ✨ LYRA • {st.session_state.cycle} — {st.session_state.niveau}")
st.caption("Ta tutrice pédagogique : elle t'aide à comprendre, pas seulement à trouver la réponse")

for m in current_messages():
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Photo
img = st.session_state.get("cam") or st.session_state.get("up")
if img and (st.session_state.get("up") is not None or st.session_state.get("cam") is not None):
    if st.button("📸 Analyser la photo"):
        ans = call_vision("Résous l'exercice sur l'image étape par étape", img.getvalue(), st.session_state.niveau)
        current_messages().append({"role": "user", "content": "📸 [Photo d'exercice]"})
        current_messages().append({"role": "assistant", "content": ans})
        set_conv_title_from_first_message("Photo d'exercice")
        st.rerun()

# Vocal
aud = st.session_state.get("aud")
if aud:
    txt = transcribe(aud.getvalue())
    if txt:
        current_messages().append({"role": "user", "content": f"🎙️ {txt}"})
        set_conv_title_from_first_message(txt)
        if detect_crisis(txt):
            current_messages().append({"role": "assistant", "content": CRISIS_MESSAGE})
            st.rerun()
        else:
            with st.chat_message("assistant"):
                full = st.write_stream(stream_text(txt, st.session_state.niveau, st.session_state.cycle))
            current_messages().append({"role": "assistant", "content": full})
            st.rerun()
    else:
        st.warning("Je n'ai pas réussi à comprendre l'audio, réessaie ou écris ta question.")

q = st.chat_input(f"Question de {st.session_state.niveau}...")
if q:
    doc_text = ""
    doc_file = st.session_state.get("doc")
    if doc_file is not None:
        doc_text = extract_document_text(doc_file)

    current_messages().append({"role": "user", "content": q + (f"\n\n📄 *(avec {doc_file.name})*" if doc_file is not None else "")})
    set_conv_title_from_first_message(q)
    with st.chat_message("user"):
        st.markdown(q)

    if detect_crisis(q):
        current_messages().append({"role": "assistant", "content": CRISIS_MESSAGE})
    else:
        with st.chat_message("assistant"):
            full = st.write_stream(stream_text(q, st.session_state.niveau, st.session_state.cycle, extra_context=doc_text))
        current_messages().append({"role": "assistant", "content": full})
    st.rerun()

st.markdown('<div class="lyra-footer">LYRA est une IA et peut faire des erreurs — vérifie les points importants avec ton professeur.</div>', unsafe_allow_html=True)
