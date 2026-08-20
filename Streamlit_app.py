import streamlit as st
import requests, os, base64, urllib.parse, random
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI - The Future of Learning", page_icon="🧬", layout="wide")

def get_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    return os.getenv("GROQ_API_KEY","")
KEY=get_key()

# --- CSS PREMIUM PAGE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter:wght@400;600&display=swap');
.stApp{background:#FFFFFF!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.block-container{padding-top:0!important;max-width:1100px!important;}

.navbar{display:flex;justify-content:space-between;align-items:center;padding:18px 0;border-bottom:1px solid #eee;}
.nav-logo{font-family:Space Grotesk;font-weight:800;font-size:24px;letter-spacing:-1px;}
.nav-links{font-family:Inter;font-size:14px;color:#666;display:flex;gap:28px;}
.hero{display:flex;align-items:center;justify-content:space-between;padding:60px 0 40px 0;}
.hero h1{font-family:Space Grotesk;font-size:64px;font-weight:800;line-height:0.95;letter-spacing:-3px;}
.hero p{font-family:Inter;font-size:18px;color:#666;margin-top:18px;line-height:1.5;}
.btn-primary{background:#111;color:white;padding:14px 28px;border-radius:100px;font-weight:600;border:none;cursor:pointer;}
.btn-secondary{background:#F3F3F3;color:#111;padding:14px 28px;border-radius:100px;font-weight:600;border:none;margin-left:10px;}
.feature-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:30px 0;}
.feature-card{background:#FAFAF8;border:1px solid #EAEAEA;border-radius:20px;padding:22px;}
.feature-card h3{font-family:Space Grotesk;font-size:18px;margin:0 0 6px 0;}
.feature-card p{font-family:Inter;font-size:13px;color:#666;margin:0;}
.footer{margin-top:60px;padding:30px 0;border-top:1px solid #eee;text-align:center;font-family:Inter;font-size:12px;color:#999;}

@keyframes replicate {
  0%{transform: rotateY(0deg) scale(1);}
  100%{transform: rotateY(360deg) scale(1);}
}
.dna-wrap{width:220px;height:220px;border-radius:50%;background:radial-gradient(circle at 30% 30%, #fff, #F0EDE8);border:1px solid #EAEAEA;display:flex;align-items:center;justify-content:center;position:relative;box-shadow:0 20px 40px rgba(0,0,0,0.06);}
</style>
""", unsafe_allow_html=True)

def ask_groq(prompt):
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+KEY},json={"model":"openai/gpt-oss-20b","messages":[{"role":"system","content":"You are NEXA-AI, a premium fast energetic AI tutor, polyglot, expert worldwide. Be concise, powerful."},{"role":"user","content":prompt}]},timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def speak_fast(text,kid):
    safe=text.replace("`"," ").replace("'"," ").replace('"'," ").replace("\n"," ")[:1800]
    html="""
    <div style="display:flex;align-items:center;gap:8px;margin-top:8px">
    <button onclick="sp_%s()" style="background:#111;color:white;border:none;border-radius:100px;padding:8px 16px;font-size:12px;font-weight:600;cursor:pointer;">▶ PLAY NEXA</button>
    <span style="font-size:11px;color:#999;">Fast voice x1.2</span>
    </div>
    <script>
    function sp_%s(){
        window.speechSynthesis.cancel();
        var t=`%s`;
        var u=new SpeechSynthesisUtterance(t);
        u.lang='fr-FR';
        u.rate=1.25;
        u.pitch=1.1;
        u.volume=1;
        var vs=window.speechSynthesis.getVoices();
        var v=vs.find(x=>x.name.includes('Google') && x.lang.includes('fr')) || vs.find(x=>x.lang=='fr-FR') || vs[0];
        if(v) u.voice=v;
        window.speechSynthesis.speak(u);
    }
    </script>
    """%(kid,kid,safe)
    components.html(html,height=55)

# --- REAL HEADER ---
st.markdown("""
<div class="navbar">
  <div class="nav-logo">NEXA-AI</div>
  <div class="nav-links"><span>Product</span><span>Solutions</span><span>Pricing</span><span>Docs</span></div>
  <div style="background:#111;color:white;padding:8px 18px;border-radius:100px;font-size:13px;font-weight:600;">Launch App</div>
</div>
""", unsafe_allow_html=True)

# --- HERO WITH REAL DNA LOGO ---
col_text, col_logo = st.columns([1.2,0.8])
with col_text:
    st.markdown("""
    <div class="hero">
