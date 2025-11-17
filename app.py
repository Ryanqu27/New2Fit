import streamlit as st
import Camera.AICamera as AICam
import Questionnaire.questionnaire as questionnaire
import DataBaseManaging.SupaBase as dataBase
import pandas as pd
import pydeck as pdk
import webbrowser
import time

# Login Handling
if not st.user.is_logged_in:
    st.title("Welcome to New2Fit!")
    st.write("Please log in to continue")
    if st.button("Log in with Google"):
        st.login("google")
    st.stop()


# Main App
st.title(f"Welcome {st.user.name}!")
dataBase.addUser(st.user.email, st.user.name)
if st.sidebar.button("Log out"):
    st.logout()
    st.stop()

if "completed_questionnaire" not in st.session_state:
    st.session_state["completed_questionnaire"] = False 
Home, AICamera, findGyms, logWorkouts = st.tabs(["      Home", "      AICamera", "      Find Gyms", "      Workouts"]) # 6 spaces aligns text to middle of tab

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
            dataBase.addUserPoints(st.user.email, st.user.name, pointAmount=10)
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

with logWorkouts:
    st.title("Log your workouts here to track your progress!")
    if "addingWorkout" not in st.session_state:
        st.session_state["addingWorkout"] = False
    if st.button("Enter a new workout"):
        st.session_state["addingWorkout"] = True
    if st.session_state["addingWorkout"]:
        date = st.date_input("When did u complete this workout?")
        dateStr = date.isoformat()
        duration = st.slider(label="Enter your workout duration in minutes", min_value=0, max_value=300)
        notes = st.text_input("Enter any notes or notable things for your workout", max_chars=300)
        exercises = st.text_input("Enter your exercises, sets, and reps here", max_chars=600)
        if st.button("Log workout"):
            dataBase.logWorkout(st.user.email, st.user.name, dateStr, duration, notes, exercises)
            st.success("Logged Workout Sucessfully!")
            st.session_state["addingWorkout"] = False
            time.sleep(1)
            st.rerun()
    if "viewingWorkouts" not in st.session_state:
        st.session_state["viewingWorkouts"] = False
    
    if st.session_state["viewingWorkouts"]:
        if st.button("Finish viewing workout"):
            st.session_state["viewingWorkouts"] = False
            st.rerun()
        workouts = dataBase.getUserWorkouts(st.user.email, st.user.name)
        if not workouts:
            st.text("No workouts available")
        else:
            for workout in workouts:
                st.text("Workout date: " + str(workout["date"])[:10])
                st.text("Exercises: " + workout["exercises"])
                st.text("Workout duration: " + str(workout["duration_minutes"]) + " minutes")
                st.text("Workout notes: " + workout["notes"])
                st.divider()
    else:
        if st.button("View logged workouts"):
            st.session_state["viewingWorkouts"] = True
            st.rerun()
        