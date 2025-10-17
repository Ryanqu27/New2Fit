import streamlit as st
import Camera.AICamera as AICam
import Questionnaire.questionnaire as questionnaire



if "completed_questionnaire" not in st.session_state:
    st.session_state["completed_questionnaire"] = False
    
Home, AICamera = st.tabs(["      Home", "      AICamera"]) # 6 spaces aligns text to middle of tab

with Home:
    # Home page either shows questionnaire or workout depending on questionnaire completion
    if not (st.session_state.get("completed_questionnaire")):
        total_score = 0
        st.header("Take our questionnaire to personalize your workouts!")
        for question in questionnaire.questions:
            user_response = st.radio( question.get_question(), question.get_answers())
            total_score += question.get_score_of_response(user_response)
            st.divider()
        if st.button("Submit questionnaire"):
            workout = questionnaire.get_workout(total_score)
            st.session_state["completed_questionnaire"] = True
            st.session_state["workout"] = workout
            st.rerun()
    else:
        st.header("Here is your recommended workout plan! Feel free to change exercises as necessary.")
        for day_key in st.session_state.get("workout"):
            st.subheader(day_key)
            st.text(st.session_state.get("workout").get(day_key))
            st.divider()
        if st.button("Retake questionnaire"):
            st.session_state["completed_questionnaire"] = False
            st.rerun()
            
with AICamera:  
    #try:
    if st.button("Open Camera"):
        AICam.run_camera()
    #except AICam.tk.TclError as e:
        #st.text("Camera is already running")
    
            
    
            