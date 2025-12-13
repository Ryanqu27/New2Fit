import streamlit as st
import Camera.AICamera as AICam
import Questionnaire.questionnaire as questionnaire
import DataBaseManaging.SupaBase as dataBase
import pandas as pd
import pydeck as pdk
import webbrowser
import time
from datetime import date

# Login Handling
if not st.user.is_logged_in:
    st.title("Welcome to New2Fit!")
    st.write("Please log in to continue")
    if st.button("Log in with Google"):
        st.login("google")
    st.stop()


# Main App
st.set_page_config( #Widen tab space
    page_title="New2Fit",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(f"Welcome {st.user.name}!")
dataBase.addUser(st.user.email, st.user.name)
today = date.today().isoformat()
last_login = dataBase.getLastLogin(st.user.email, st.user.name)
if last_login != today:
    dataBase.addUserPoints(st.user.email, st.user.name, 5)
    dataBase.updateLastLogin(st.user.email, st.user.name)
if st.sidebar.button("Log out"):
    st.logout()
    st.stop()

if "completed_questionnaire" not in st.session_state:
    st.session_state["completed_questionnaire"] = False 
Home, AICamera, findGyms, logWorkouts, progress = st.tabs(["      Home", "      AICamera", "      Find Gyms", "      Workouts", "      Progress"]) # 6 spaces aligns text to middle of tab

with Home:
    # Home page either shows questionnaire or workout depending on questionnaire completion
    if not (st.session_state.get("completed_questionnaire")):
        totalScore = 0
        st.header("Take our questionnaire to get a workout recommendation!")
        st.divider()
        for question in questionnaire.questions:
            userResponse = st.radio( question.get_question(), question.get_answers())
            totalScore += question.get_score_of_response(userResponse)
            st.divider()
        if st.button("Submit questionnaire", icon="✅"):
            workout = questionnaire.get_workout(totalScore)
            st.session_state["completed_questionnaire"] = True
            st.session_state["workout"] = workout
            st.rerun()
    else:
        st.header("Here is your recommended weekly workout plan! Feel free to change exercises as necessary.")
        for day_key in st.session_state.get("workout"):
            st.subheader(day_key)
            st.text(st.session_state.get("workout").get(day_key))
            st.divider()
        if st.button("Retake questionnaire", icon="🔄"):
            st.session_state["completed_questionnaire"] = False
            st.rerun()
            
with AICamera:
    st.header("AI Form Analysis")
    st.subheader("Select an exercise and use your camera to analyze movement and form in real time.")
    st.divider()

    st.subheader("Choose an Exercise")

    exercise = st.radio(
        label="Select exercise",
        options=["Bicep Curls", "Lateral Raises"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.divider()
    st.subheader("Start Camera")
    try:
        if st.button(
            "Open Camera",
            icon="📷",
            use_container_width=True
        ):
            AICam.run_camera(exercise=exercise)
            dataBase.addUserPoints(
                st.user.email,
                st.user.name,
                pointAmount=10
            )

    except AICam.tk.TclError:
        st.warning("Camera is already running.")
                    


with findGyms:
    st.header("Find the right gym for you with our gym locator")
    st.divider() 

    gyms = pd.read_csv("GymLocations/Gyms.csv")
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
        if st.button("Open Gym Website", icon="🌐"):
            webbrowser.open_new_tab(gymURL)

with logWorkouts:
    st.header("Log Your Workouts")
    st.subheader("Track your training and monitor progress over time.")
    st.divider()

    st.session_state.setdefault("addingWorkout", False)
    st.session_state.setdefault("viewingWorkouts", False)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Log New Workout", use_container_width=True):
            st.session_state["addingWorkout"] = True
            st.session_state["viewingWorkouts"] = False

    with col2:
        if st.button("📖 View Workout History", use_container_width=True):
            st.session_state["viewingWorkouts"] = True
            st.session_state["addingWorkout"] = False

    if st.session_state["addingWorkout"]:
        st.subheader("New Workout Entry")

        with st.form("log_workout_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                date = st.date_input("📅 Workout Date")

            with col2:
                duration = st.slider(
                    "⏱ Duration (minutes)",
                    min_value=0,
                    max_value=300,
                    step=5
                )

            exercises = st.text_area(
                "🏋️ Exercises (sets × reps)",
                placeholder="Bench Press 3x8 100lbs, Squats 4x5...",
                max_chars=600
            )

            notes = st.text_area(
                "📝 Notes",
                placeholder="How did it feel? PRs? Fatigue?",
                max_chars=300
            )

            submitted = st.form_submit_button("✅ Log Workout")

            if submitted:
                dataBase.logWorkout(
                    st.user.email,
                    st.user.name,
                    date.isoformat(),
                    duration,
                    notes,
                    exercises
                )
                dataBase.addUserPoints(
                    st.user.email,
                    st.user.name,
                    pointAmount=20
                )

                st.success("Workout logged successfully!")
                st.session_state["addingWorkout"] = False
                time.sleep(0.8)
                st.rerun()

    if st.session_state["viewingWorkouts"]:
        st.subheader("Your Workout History")

        workouts = dataBase.getUserWorkouts(st.user.email, st.user.name)

        if not workouts:
            st.info("No workouts logged yet. Start by adding one!")
        else:
            for workout in workouts:
                with st.expander(f"📅 {workout['date']} — ⏱ {workout['duration_minutes']} min"):
                    st.markdown(f"**Exercises:**\n\n{workout['exercises']}")
                    st.markdown(f"**Notes:**\n\n{workout['notes']}")



with progress:
    st.header("Check your progress here!")
    st.divider()
    points = dataBase.getUserPoints(st.user.email, st.user.name)
    level = points // 100
    current_level_points = points - (level * 100)
    points_to_next = 100 - current_level_points
    st.columns(2)[0].metric("Level", level)
    st.columns(2)[1].metric("Points", points)
    pct = current_level_points / 100 if points >= 0 else 0.0
    st.progress(pct)
    st.caption(f"{current_level_points} / 100 pts to next level — {points_to_next} pts remaining")
    