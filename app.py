import streamlit as st
import Camera.AICamera as AICam
import Questionnaire.questionnaire as questionnaire
import pandas as pd
import pydeck as pdk
import webbrowser

# Login Handling
if not st.user.is_logged_in:
    st.title("Welcome to New2Fit!")
    st.write("Please log in to continue")
    if st.button("Log in with Google"):
        st.login("google")
    st.stop()


# Main App
st.title(f"Welcome {st.user.name}!")
if st.sidebar.button("Log out"):
    st.logout()
    st.stop()

if "completed_questionnaire" not in st.session_state:
    st.session_state["completed_questionnaire"] = False 
Home, AICamera, findGyms = st.tabs(["      Home", "      AICamera", "      Find Gyms"]) # 6 spaces aligns text to middle of tab

with Home:
    # Home page either shows questionnaire or workout depending on questionnaire completion
    if not (st.session_state.get("completed_questionnaire")):
        totalScore = 0
        st.header("Take our questionnaire to personalize your workouts!")
        for question in questionnaire.questions:
            userResponse = st.radio( question.get_question(), question.get_answers())
            totalScore += question.get_score_of_response(userResponse)
            st.divider()
        if st.button("Submit questionnaire"):
            workout = questionnaire.get_workout(totalScore)
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
    st.title("Use our AI Camera to track and analyze form in real-time") 
    try:
        if st.button("Open Camera"):
            AICam.run_camera()
    except AICam.tk.TclError as e:
        st.text("Camera is already running")

with findGyms:
    gyms = pd.read_csv("GymLocations/CrunchGyms.csv")
    pointLayer = pdk.Layer(
        "ScatterplotLayer", 
        data=gyms, 
        id="gymLocation",
        get_position=["longitude", "latitude"], 
        pickable=True, 
        get_radius=2500,
        get_color=[200, 75, 75]
    )
    initialViewState = pdk.ViewState (
        latitude =40, longitude = -100, controller=True, zoom = 3.5, pitch=30
    )
    chart = pdk.Deck(
        layers=[pointLayer], 
        initial_view_state=initialViewState, 
        tooltip={"text": "{city}, {state}\n Gym Website: {URL}"}
    )
        
    
    event = st.pydeck_chart(chart, on_select="rerun", selection_mode="single-object")
    
    if event and event.selection["objects"]:
        clicked = event.selection
        gymData = clicked["objects"].get("gymLocation")[0]
        gymCity = gymData["city"]
        gymURL = gymData["URL"]
        gymBrand = gymData["brand"]
        st.success(f"You selected a {gymBrand} gym in {gymCity}")
        if st.button("Open Gym Website"):
            webbrowser.open_new_tab(gymURL)
                            