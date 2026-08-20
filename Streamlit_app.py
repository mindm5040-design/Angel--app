import streamlit.components.v1 as components

components.html("""
<div style="display:flex; flex-direction:column; align-items:center; background:#fcfcf9; padding:30px; border-radius:24px; font-family:sans-serif;">
<style>
  .brain-wrap {width:140px; height:140px; position:relative;}
  .brain-outline {position:absolute; inset:0; z-index:2; pointer-events:none;}
  .neurons {position:absolute; inset:12%; z-index:1; animation: spin 10s linear infinite; transform-origin:center;}
  @keyframes spin {from{transform:rotate(0deg)} to{transform:rotate(360deg)}}
  .node {animation: glow 1.8s ease-in-out infinite;}
  .node:nth-child(odd){animation-delay:0.3s}
  @keyframes glow {0%,100%{opacity:0.8; filter:brightness(1)} 50%{opacity:1; filter:brightness(1.5) drop-shadow(0 0 6px #E07A4F)}}
  .link {stroke-dasharray: 4 4; animation: dash 2s linear infinite;}
  @keyframes dash {to{stroke-dashoffset:-20}}
</style>

<div class="brain-wrap">
  <!-- CERVEAU CONTOUR FIXE -->
  <svg class="brain-outline" viewBox="0 0 100 100">
    <path d="M 20 35 C 10 20, 35 5, 50 18 C 65 5, 90 20, 80 35 C 95 40, 90 65, 75 68 C 78 85, 55 85, 50 70 C 45 85, 22 85, 25 68 C 10 65, 5 40, 20 35 Z" 
    fill="none" stroke="#0a0a0a" stroke-width="2.5" stroke-linecap="round"/>
  </svg>

  <!-- NEURONES QUI TOURNENT À L'INTÉRIEUR -->
  <svg class="neurons" viewBox="0 0 100 100">
    <g stroke="#E07A4F" stroke-width="1" opacity="0.6">
      <line class="link" x1="20" y1="30" x2="50" y2="20"/>
      <line class="link" x1="50" y1="20" x2="80" y2="30"/>
      <line class="link" x1="80" y1="30" x2="70" y2="60"/>
      <line class="link" x1="70" y1="60" x2="40" y2="70"/>
      <line class="link" x1="40" y1="70" x2="20" y2="30"/>
      <line class="link" x1="20" y1="30" x2="70" y2="60"/>
      <line class="link" x1="50" y1="20" x2="40" y2="70"/>
    </g>
    <circle class="node" cx="20" cy="30" r="5" fill="#E07A4F"/>
    <circle class="node" cx="50" cy="20" r="6" fill="#E07A4F"/>
    <circle class="node" cx="80" cy="30" r="5" fill="#E07A4F"/>
    <circle class="node" cx="70" cy="60" r="7" fill="#E07A4F"/>
    <circle class="node" cx="40" cy="70" r="5" fill="#E07A4F"/>
    <circle class="node" cx="50" cy="45" r="4" fill="#0a27a6"/>
  </svg>
</div>

<div style="margin-top:16px; font-size:28px; font-weight:700; letter-spacing:-1px; color:#0a0a0a;">Angel AI</div>
<div style="font-size:10px; letter-spacing:3px; color:#999; font-weight:700; margin-top:4px;">NEURAL • LEARNING</div>
</div>
""", height=260)
