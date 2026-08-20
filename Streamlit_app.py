import streamlit as st
import requests, os, base64, random, urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI", page_icon="NEXA", layout="wide")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY","")

KEY=get_key()

# DESIGN HIGH TECH - SANS TRIPLE GUILLEMETS
css = "<style>"
css += "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@400&display=swap');"
css += ".stApp{background:#07070A!important;color:white!important;}"
css += "header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}"
css += ".block-container{max-width:1200px!important;padding-top:0!important;}"
css += ".navbar{display:flex;justify-content:space-between;align-items:center;padding:20px 0;border-bottom:1px solid #1A1A1F;}"
css += ".logo{font-family:Space Grotesk;font-weight:800;font-size:26px;letter-spacing:-1px;color:white;}"
css += ".logo span{color:#FF5C00;}"
css += ".hero{padding:80px 0 40px 0;display:flex;justify-content:space-between;align-items:center;}"
css += ".hero h1{font-family:Space Grotesk;font-size:72px;font-weight:800;line-height:0.9;letter-spacing:-4px;color:white;}"
css += ".hero h1 span{background:linear-gradient(90deg,#FF5C00,#FF8A00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}"
css += ".hero p{font-family:JetBrains Mono;font-size:14px;color:#888;margin-top:20px;max-width:420px;line-height:1.6;}"
css += ".card{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:20px;backdrop-filter:blur(20px);}"
css += ".btn{border-radius:100px;padding:12px 24px;font-weight:700;font-size:13px;border:none;cursor:pointer;}"
css += ".btn-main{background:white;color:black;}"
css += ".btn-ghost{background:rgba(255,255,255,0.08);color:white;margin-left:8px;}"
css += "@keyframes dna{0%{transform:rotateY(0deg)}100%{transform:rotateY(360deg)}}"
css += "</style>"

st.markdown(css, unsafe_allow_html=True)

def ask(prompt):
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+KEY},json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":"You are NEXA-AI, high-tech AI, fast, concise, futuristic."},{"role":"user","content":prompt}]},timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def voice(text,kid):
    safe=text.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:1500]
    h = "<button onclick='v%s()' style='background:#FF5C00;color:white;border:none;border-radius:100px;padding:8px 16px;font-weight:700;cursor:pointer;'>PLAY x1.3</button>" % kid
    h += "<script>function v%s(){window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(`%s`);u.rate=1.35;u.pitch=1.05;u.volume=1;u.lang='fr-FR';window.speechSynthesis.speak(u);}</script>" % (kid,safe)
    components.html(h,height=50)

# HEADER
st.markdown('<div class="navbar"><div class="logo">NEXA<span>-AI</span></div><div style="font-family:JetBrains Mono;font-size:11px;color:#666;">SYSTEM ONLINE // v2.0</div><div style="background:white;color:black;padding:8px 18px;border-radius:100px;font-weight:700;font-size:12px;">LAUNCH APP</div></div>', unsafe_allow_html=True)

# HERO
c1,c2 = st.columns([1.2,0.8])
with c1:
    st.markdown('<div class="hero"><div><h1>THE<br>INTELLIGENCE<br><span>THAT REPLICATES.</span></h1><p>NEXA-AI is a high-tech learning engine. Photo correction, PDF generation, timed exams, visual schemas, fast voice, group mode. No fluff. Just intelligence.</p><div style="margin-top:24px;"><span class="btn btn-main">START FREE</span><span class="btn btn-ghost">WATCH DEMO</span></div></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="width:320px;height:320px;border-radius:50%;background:radial-gradient(circle at 30% 30%, #1A1A1F, #07070A);border:1px solid #222;display:flex;align-items:center;justify-content:center;position:relative;margin:auto;box-shadow:0 0 80px rgba(255,92,0,0.15);"><div style="animation:dna 3s linear infinite;"><svg width="180" height="180" viewBox="0 0 100 100"><path d="M20 10 Q50 20 80 10" stroke="#FF5C00" stroke-width="2" fill="none"/><path d="M20 30 Q50 40 80 30" stroke="white" stroke-width="2" fill="none"/><path d="M20 50 Q50 60 80 50" stroke="#FF5C00" stroke-width="2" fill="none"/><path d="M20 70 Q50 80 80 70" stroke="white" stroke-width="2" fill="none"/><line x1="30" y1="14" x2="70" y2="14" stroke="#FF5C00" stroke-width="1"/><line x1="30" y1="34" x2="70" y2="34" stroke="white" stroke-width="1"/><line x1="30" y1="54" x2="70" y2="54" stroke="#FF5C00" stroke-width="1"/><line x1="30" y1="74" x2="70" y2="74" stroke="white" stroke-width="1"/></svg></div><div style="position:absolute;inset:-10px;border-radius:50%;border:1px dashed rgba(255,92,0,0.2);animation:dna 10s linear infinite reverse;"></div></div>', unsafe_allow_html=True)

# FEATURES GRID
st.markdown('<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:20px 0;"><div class="card"><div style="color:#FF5C00;font-size:20px;">📸</div><div style="font-weight:700;margin-top:8px;">Photo Correction</div><div style="color:#777;font-size:12px;margin-top:4px;">Red pen style, score /20</div></div><div class="card"><div style="color:#FF5C00;font-size:20px;">📄</div><div style="font-weight:700;margin-top:8px;">PDF Engine</div><div style="color:#777;font-size:12px;margin-top:4px;">Revision sheets instantly</div></div><div class="card"><div style="color:#FF5C00;font-size:20px;">⏱️</div><div style="font-weight:700;margin-top:8px;">Exam Mode</div><div style="color:#777;font-size:12px;margin-top:4px;">10 timed Q + ranking</div></div></div>', unsafe_allow_html=True)

if not KEY:
    st.warning("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "exam" not in st.session_state:
    st.session_state.exam=""

st.markdown('<div style="height:1px;background:#1A1A1F;margin:20px 0;"></div>', unsafe_allow_html=True)

classe=st.selectbox("LEVEL",["Middle","High School","Bachelor","Master 1","Master 2","PhD"],index=3)
mode=st.selectbox("POWER",["Chat","Photo Fix","PDF","Exam","Visual","Ranking","WhatsApp","Group"])

if mode=="Chat":
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"]=="assistant":
                voice(m["content"],i)
    p=st.chat_input("Ask NEXA...")
    if p:
        st.session_state.messages.append({"role":"user","content":p})
        with st.chat_message("user"):
            st.markdown(p)
        with
