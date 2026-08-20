import streamlit as st
import requests, base64, streamlit.components.v1 as components

st.set_page_config(page_title="Angel AI v4.0", page_icon="🕊️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@600;800&display=swap');
.stApp {background:#020617!important;}
header, footer {visibility:hidden!important;}
</style>
""", unsafe_allow_html=True)

KEY = st.secrets.get("GROQ_API_KEY","")
if "classe" not in st.session_state: st.session_state.classe=None
if "messages" not in st.session_state: st.session_state.messages=[]

# --- ANIMATION HOLOGRAMME CARTE CAMEROUN ---
HOLO_HTML = """
<div id="holo">
<style>
#holo {position:relative; width:100%; height:420px; background: radial-gradient(ellipse at center, #0a2540 0%, #020617 70%); border:1px solid #0ff3; border-radius:20px; overflow:hidden; font-family:'JetBrains Mono', monospace;}
.scanline {position:absolute; width:100%; height:2px; background:linear-gradient(90deg, transparent, #00e5ff, transparent); animation: scan 3s linear infinite; z-index:10;}
@keyframes scan {0%{top:0} 100%{top:100%}}

.map-wrap {position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); width:300px; height:420px;}
.map-svg {width:100%; height:100%; filter: drop-shadow(0 0 15px #00e5ff) drop-shadow(0 0 30px #00e5ff66);}
.map-path {fill:none; stroke:#00e5ff; stroke-width:1.2; stroke-dasharray:1000; stroke-dashoffset:1000; animation: draw 2.5s ease forwards, glow 2s ease-in-out infinite alternate; opacity:0.9;}
@keyframes draw {to {stroke-dashoffset:0;}}
@keyframes glow {0%{stroke-width:1.2; filter:brightness(1);} 100%{stroke-width:1.8; filter:brightness(1.4);}}

.node {position:absolute; width:10px; height:10px; background:#00e5ff; border-radius:50%; box-shadow:0 0 10px #00e5ff, 0 0 20px #00e5ff; animation: pulse 1.5s infinite;}
.node::after {content:''; position:absolute; width:24px; height:24px; border:1px solid #00e5ff; border-radius:50%; left:-7px; top:-7px; animation: ripple 2s infinite;}
@keyframes pulse {0%,100%{transform:scale(1);} 50%{transform:scale(1.3);}}
@keyframes ripple {0%{transform:scale(0.5); opacity:1;} 100%{transform:scale(2); opacity:0;}}

.label {position:absolute; color:#7dd3fc; font-size:10px; font-weight:700; text-shadow:0 0 8px #00e5ff; letter-spacing:1px; animation: flicker 3s infinite;}
@keyframes flicker {0%,100%{opacity:1;} 50%{opacity:0.7;}}

.grid {position:absolute; bottom:0; width:100%; height:80px; background: repeating-linear-gradient(90deg, #00e5ff11 0 1px, transparent 1px 40px), radial-gradient(ellipse at center, #00e5ff22 0%, transparent 70%); animation: gridMove 4s linear infinite;}
@keyframes gridMove {0%{transform:perspective(200px) rotateX(60deg) translateY(0);} 100%{transform:perspective(200px) rotateX(60deg) translateY(40px);}}

.title {position:absolute; top:14px; left:16px; color:#00e5ff; font-size:13px; font-weight:800; letter-spacing:2px; text-shadow:0 0 10px #00e5ff;}
</style>
<div class="scanline"></div>
<div class="title">IA CAMEROUN v4.0 • ANGEL AI • SYSTEM ONLINE</div>

<div class="map-wrap">
<svg class="map-svg" viewBox="0 0 100 140" xmlns="http://www.w3.org/2000/svg">
<!-- Forme simplifiée Cameroun -->
<path class="map-path" d="M 35 2 L 55 5 L 62 18 L 68 22 L 72 35 L 70 48 L 65 58 L 68 70 L 70 85 L 68 100 L 65 115 L 60 125 L 45 128 L 30 124 L 25 110 L 20 95 L 18 80 L 15 65 L 18 50 L 22 35 L 28 15 Z" />
</svg>
<div class="node" style="left:48%; top:82%;"></div>
<div class="label" style="left:48%; top:90%;">YAOUNDÉ • HUB</div>

<div class="node" style="left:22%; top:68%;"></div>
<div class="label" style="left:2%; top:68%;">DOUALA</div>

<div class="node" style="left:28%; top:42%;"></div>
<div class="label" style="left:2%; top:38%;">BAMENDA</div>
</div>

<div class="grid"></div>
</div>
"""

if st.session_state.classe is None:
    components.html(HOLO_HTML, height=440)

    st.markdown("""
    <div style='text-align:center; margin-top:16px;'>
    <div style='font-family:Outfit; font-size:28px; font-weight:800; background:linear-gradient(90deg,#00e5ff,#a5f3fc,#00e5ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-size:200%; animation: shine 3s linear infinite;'>Choisis ton niveau pour activer le réseau</div>
    <div style='color:#64748b; font-family:JetBrains Mono; font-size:11px; letter-spacing:2px; margin-top:6px;'>MODÈLE IA LOCAL • FR/EN/FULFULDE • SYNC 100%</div>
    </div>
    <style>@keyframes shine{to{background-position:200% center;}}</style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='color:#00e5ff; font-size:11px; font-weight:800; letter-spacing:2px; margin:20px 0 8px; font-family:JetBrains Mono;'>COLLÈGE • RÉSEAU NORD</div>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    for i, cl in enumerate(["6e","5e","4e","3e"]):
        with [c1,c2,c3,c4][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div style='color:#00e5ff; font-size:11px; font-weight:800; letter-spacing:2px; margin:16px 0 8px; font-family:JetBrains Mono;'>LYCÉE • RÉSEAU CENTRE</div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for i, cl in enumerate(["Seconde","Première","Terminale"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()

    st.markdown("<div style='color:#00e5ff; font-size:11px; font-weight:800; letter-spacing:2px; margin:16px 0 8px; font-family:JetBrains Mono;'>UNIVERSITÉ • RÉSEAU NATIONAL +47% RENDEMENT</div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for i, cl in enumerate(["Licence 1","Licence 2","Licence 3"]):
        with [c1,c2,c3][i]:
            if st.button(cl, key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()
    c1,c2,c3=st.columns(3)
    for i, cl in enumerate(["Master 1","Master 2","Doctorat"]):
        with [c1,c2,c3][i]:
            if st.button(f"🚀 {cl}", key=cl, use_container_width=True):
                st.session_state.classe=cl; st.rerun()
    st.stop()

# CHAT APRES SELECTION
st.markdown(f"<div style='color:#00e5ff; font-family:JetBrains Mono; font-size:12px;'>🕊️ ANGEL • {st.session_state.classe} • NEURAL ACTIVE • YAOUNDÉ</div>", unsafe_allow_html=True)
if st.button("↩️ Retour carte"): st.session_state.classe=None; st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

prompt=st.chat_input("Message à Angel IA...")
if prompt:
    def ask(q):
        body={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":f"Tu es Angel IA v4.0 niveau {st.session_state.classe}"},{"role":"user","content":q}]}
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json=body,timeout=60).json()
        return r["choices"][0]["message"]["content"]
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.messages.append({"role":"assistant","content":ask(prompt)})
    st.rerun()
