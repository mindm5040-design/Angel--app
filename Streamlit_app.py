"""
Angel — Instrument d'étude - FIX FINAL SANS CLE
Pollinations OpenAI only + fallback
"""
import requests
import streamlit as st

st.set_page_config(page_title="Angel — Instrument d'étude", page_icon="🕊️", layout="wide", initial_sidebar_state="expanded")

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
.stApp{ background:#0a0d13; color:#edeff3; }
section[data-testid="stSidebar"]{ background:#10141c; border-right:1px solid rgba(237,239,243,0.10); }
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;}
.stButton>button{ background:#151a24; color:#edeff3; border:1px solid rgba(237,239,243,0.10); border-radius:10px; }
.halo-ring{ width:70px; height:70px; margin:0 auto 18px; }
.halo-ring svg{ animation: halo-spin 3.2s linear infinite; }
@keyframes halo-spin{ to{ transform: rotate(360deg); } }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
HALO_SVG = '<div class="halo-ring"><svg viewBox="0 0 64 64" width="70" height="70"><circle cx="32" cy="32" r="26" fill="none" stroke="rgba(237,239,243,0.18)" stroke-width="1.4"/><path d="M32 6 A26 26 0 0 1 55 20" fill="none" stroke="#ffd98a" stroke-width="2.4" stroke-linecap="round"/></svg></div>'

LEVELS_COLLEGE = ["6e","5e","4e","3e","Seconde","Première","Terminale"]
LEVELS_UNIV = ["Licence 1","Licence 2","Licence 3","Master 1","Master 2","Doctorat"]
CHIPS_COLLEGE = ["Explique-moi les fractions","Résume ce chapitre d'Histoire","Corrige ma dissertation","Prépare-moi à l'interrogation"]
CHIPS_UNIV = ["Démontre ce théorème","Structure mon plan de mémoire","Vérifie ce raisonnement","Synthétise cet article"]

for k,v in {"step":1,"cycle":None,"level":None,"first_name":"","messages":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

def call_angel_free(question, level):
    system = f"Tu es Angel, instrument d'étude académique. Niveau: {level} ({st.session_state.get('cycle')}). Réponse directe, dense, pédagogique, exclusivement scolaire."
    # FOURNISSEUR 1 - Pollinations (le plus stable)
    try:
        payload = {"model":"openai","messages":[{"role":"system","content":system},{"role":"user","content":question}],"stream":False}
        r = requests.post("https://text.pollinations.ai/openai", json=payload, timeout=60)
        if r.status_code==200:
            data=r.json()
            if "choices" in data and len(data["choices"])>0:
                return data["choices"][0]["message"]["content"]
    except: pass

    # FOURNISSEUR 2 - Pollinations GET ultra simple (fallback sans JSON)
    try:
        import urllib.parse
        full = f"{system}\n\nQuestion: {question}"
        enc = urllib.parse.quote(full[:2000])
        r = requests.get(f"https://text.pollinations.ai/{enc}", timeout=60, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code==200 and len(r.text)>10:
            return r.text
    except: pass

    raise RuntimeError("IA gratuite en surcharge 5 sec, réessaie.")

def render_onboarding():
    if st.session_state.step==1:
        st.markdown(HALO_SVG, unsafe_allow_html=True)
        st.markdown("## Choisissez votre cycle")
        c1,c2=st.columns(2)
        with c1:
            if st.button("Collège & Lycée",use_container_width=True): st.session_state.cycle="college"; st.session_state.step=2; st.rerun()
        with c2:
            if st.button("Université",use_container_width=True): st.session_state.cycle="universite"; st.session_state.step=2; st.rerun()
    elif st.session_state.step==2:
        levels=LEVELS_COLLEGE if st.session_state.cycle=="college" else LEVELS_UNIV
        st.markdown("### Ton niveau")
        cols=st.columns(4)
        for i,lv in enumerate(levels):
            with cols[i%4]:
                if st.button(lv,key=f"lv_{lv}",use_container_width=True): st.session_state.level=lv; st.session_state.step=3; st.rerun()
        if st.button("← Retour"): st.session_state.step=1; st.rerun()
    elif st.session_state.step==3:
        st.markdown("### Comment t'appeler?")
        st.session_state.first_name=st.text_input("Prénom",value=st.session_state.first_name,placeholder="Ex: Samuel")
        if st.button("Entrer dans Angel →",type="primary",use_container_width=True): st.session_state.step=4; st.rerun()

def render_chat():
    with st.sidebar:
        st.markdown(f"### 🕊️ Angel\n{st.session_state.first_name} • {st.session_state.level}")
        st.success("✅ Gratuit - Sans clé\nModèle: Llama 3.3 70B")
        if st.button("Nouvelle conversation",use_container_width=True): st.session_state.messages=[]; st.rerun()
        if st.button("Changer niveau",use_container_width=True): st.session_state.step=1; st.session_state.messages=[]; st.rerun()

    if not st.session_state.messages:
        st.markdown(HALO_SVG, unsafe_allow_html=True)
        chips=CHIPS_COLLEGE if st.session_state.cycle=="college" else CHIPS_UNIV
        cols=st.columns(4)
        for i,c in enumerate(chips):
            with cols[i]:
                if st.button(c,key=f"chip_{i}",use_container_width=True): handle(c); st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    q=st.chat_input("Écrivez votre question de cours…")
    if q: handle(q); st.rerun()

def handle(question):
    st.session_state.messages.append({"role":"user","content":question})
    with st.spinner("Angel réfléchit…"):
        try: ans=call_angel_free(question, st.session_state.level)
        except Exception as e: ans=f"Désolé, petite surcharge: {e}\nRéessaie dans 3 sec."
    st.session_state.messages.append({"role":"assistant","content":ans})

if st.session_state.step<4: render_onboarding()
else: render_chat()
