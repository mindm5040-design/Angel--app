import streamlit as st
import requests, base64

st.set_page_config(page_title="Angel", page_icon="🕊️", layout="centered")

# --- DESIGN LE PLUS AIME AU MONDE - MESSENGER ---
st.markdown("""
<style>
.stApp {background:#ffffff!important;}
header, footer, #MainMenu {visibility:hidden!important;}
div[data-testid="stChatMessages"] {max-width:720px; margin:auto;}
.stChatMessage {border:none!important; background:transparent!important;}
div[data-testid="stChatMessageContent"] {padding:0!important;}

/* BUBBLES */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{
    background:#0a27a6!important; color:white!important; 
    border-radius:18px 18px 4px 18px!important; padding:10px 14px!important; max-width:80%; margin-left:auto;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"]{
    background:#f0f2f5!important; color:black!important;
    border-radius:18px 18px 18px 4px!important; padding:10px 14px!important; max-width:80%;
}

/* BARRE BAS FIXE HORIZONTALE */
div[data-testid="stBottom"] > div {background:white!important; border-top:1px solid #e4e6eb!important; padding:8px!important;}
div[data-testid="stHorizontalBlock"]{display:flex!important; flex-direction:row!important; flex-wrap:nowrap!important; gap:6px!important; align-items:center!important;}
div[data-testid="column"] button{border-radius:50%!important; width:42px!important; height:42px!important; background:#0a27a6!important; color:white!important; border:none!important;}
button[kind="primary"]{background:#ff2e2e!important; border-radius:12px!important; width:44px!important; height:44px!important;}
input, textarea{background:#f0f2f5!important; border-radius:20px!important; border:none!important
