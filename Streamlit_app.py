import streamlit as st
import requests, base64
from pathlib import Path

st.set_page_config(page_title="Angel AI", page_icon="🧠", layout="centered")

# --- LOGO VIDEO CERVEAU QUI TOURNE ---
def get_video_base64(path):
    if Path(path).exists():
        return base64.b64encode(Path(path).read_bytes()).decode()
    return None

video_b64 = get_video_base64("brain.mp4")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=DM+Sans:wght@400;600&display=swap');
.stApp {{background:#fcfcf9!important; font-family:'DM Sans', sans-serif!important;}}
header, footer, #MainMenu {{visibility:hidden!important;}}
.angel-hero {{font-family:'Space Grotesk', sans-serif; font-size:42px; font-weight:700; letter-spacing:-2px; color:#0a0a0a; line-height:0.9; margin:10px 0 4px; text-align:center;}}
.brain-container {{display:flex; justify-content:center; margin:10px 0 20px;}}
.brain-video {{width:140px; height:140px; border-radius:50%; object-fit:cover; box-shadow:0 0 40px rgba(224,122,79,0.3), 0 8px 24px rgba(0,0,0,0.15); border:2px solid #E07A4F;}}
div[data-testid="stButton"] > button {{
  background: rgba(255,255,255,0.7)!important; backdrop-filter: blur(20px) saturate(180%)!important;
  border:1px solid rgba(0,0,0,0.08)!important; border-radius:18px!important; height:72px!important;
  font-family:'Space Grotesk', sans-serif!important; font-weight:600!important; font-size:16px!important;
  color:#0a0a0a!important; box-shadow: 0 4px 12px rgba(0,0,0,0.04)!important;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)!important;
}}
div[data-testid="stButton"] > button:hover {{transform: perspective(600px) rotateX(4deg) rotateY(-4deg) translateY(-4px) scale(1.02)!important; box-shadow: 0 20px 40px rgba(0,0,0,0.1)!important;}}
button[kind="primary"] {{background: #0a0a0a!important; color:white!important; border:none!important;}}
</style>

<div class="brain-container">
  {"<video class='brain-video' autoplay loop muted playsinline><source src='data:video/mp4;base64,"+video_b64+"' type='video/mp4'></video>" if video_b64 else "<div style='font-size:80px;'>🧠</div>"}
</div>
<div class="angel-hero">Angel AI</div>
<div style="text-align:center; color:#E07A4F; font-size:10px; letter-spacing:3px; font-weight:700; margin-bottom:24px;">NEURAL ENGINE • ACTIVE</div>
""", unsafe_allow_html=True)

KEY = st.se
