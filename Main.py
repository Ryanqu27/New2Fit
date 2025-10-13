import streamlit as st
import Camera.AICamera as AICam
import Questionnaire.questionnaire as questionnaire

Home, AICamera = st.tabs(["      Home", "      AICamera"]) # 6 spaces aligns text to middle of tab

questionnaire.questions

with AICamera:  
    try:
        if st.button("Open Camera"):
            AICam.run_camera()     
    except AICam.tk.TclError as e:
        st.text("Camera is already running")
    
            
    
            