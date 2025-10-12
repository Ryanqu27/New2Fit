import streamlit as st
import Camera.AICamera as AICamera

Home, AICamera = st.tabs(["      Home", "      AICamera"]) # 6 spaces aligns text to middle of tab


with AICamera:  
    try:
        if st.button("Open Camera"):
            AICamera.run_camera()     
    except AICamera.tk.TclError as e:
        st.text("Camera is already running")
    
            
    
            