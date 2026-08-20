prompt=st.chat_input(f"Question niveau {st.session_state.classe}...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # --- ANIMATION REFLEXION ---
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("""
    <div style="display:flex; align-items:center; gap:12px; background:white; border-radius:20px; padding:14px 18px; border:1px solid #eee; margin-top:10px;">
      <div style="width:36px;height:36px;border-radius:50%;background:#E07A4F;display:flex;align-items:center;justify-content:center;animation: pulse 1.2s infinite;">🧠</div>
      <div>
        <div style="font-family:'Space Grotesk';font-weight:600;">Angel réfléchit</div>
        <div style="display:flex; gap:4px; margin-top:4px;">
          <span style="width:6px;height:6px;background:#E07A4F;border-radius:50%;animation: bounce 1.4s infinite;"></span>
          <span style="width:6px;height:6px;background:#E07A4F;border-radius:50%;animation: bounce 1.4s infinite 0.2s;"></span>
          <span style="width:6px;height:6px;background:#E07A4F;border-radius:50%;animation: bounce 1.4s infinite 0.4s;"></span>
        </div>
      </div>
    </div>
    <style>
    @keyframes pulse {0%{transform:scale(1)}50%{transform:scale(1.15)}100%{transform:scale(1)}}
    @keyframes bounce {0%,80%,100%{transform:translateY(0);opacity:0.5}40%{transform:translateY(-6px);opacity:1}}
    </style>
    """, unsafe_allow_html=True)
    
    rep=ask_groq(prompt)
    thinking_placeholder.empty()
    
    st.session_state.messages.append({"role":"assistant","content":rep})
    with st.chat_message("assistant"):
        st.markdown(rep)
