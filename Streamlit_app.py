import streamlit as st
import requests, os, random, urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="NEXA-AI ⚡", page_icon="⚡", layout="centered")

def get_key():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except:
        return os.getenv("OPENROUTER_API_KEY","")

KEY=get_key()

st.markdown("""
<style>
.stApp{background:#0F0F1A!important;color:white!important;}
header,footer,#MainMenu,.stDeployButton{visibility:hidden!important;}
.nexa-title{font-size:42px;font-weight:800;text-align:center;background: linear-gradient(90deg, #7F5AF0, #2CB67D);-webkit-background-clip: text;-webkit-text-fill-color: transparent;}
.mode-card{background:#1F1F2E;border:
