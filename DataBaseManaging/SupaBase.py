import streamlit as st
from supabase import create_client, Client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def getUserPoints(userEmail, userName) ->int:
    response = supabase.rpc("get_user_points", {
        "useremail": userEmail,
        "username": userName
    }).execute()
    return response.data

def addUser(userEmail, userName):
    points = getUserPoints(userEmail, userName)
    # If points does not exist, user is not in data base system.
    if points is None:
        supabase.rpc("add_user", {
                "useremail": userEmail, 
                "username": userName
                }).execute()

def addUserPoints(userEmail, userName, pointAmount):
    supabase.rpc("add_points", {
        "useremail": userEmail,
        "username": userName,
        "pointamount": pointAmount
    }).execute()

def logWorkout(userEmail, userName, date, duration, notes, exercises):
    supabase.rpc("log_workout", {
        "p_username": userName,
        "p_useremail": userEmail,
        "p_date":date,
        "p_duration": duration,
        "p_notes":notes,
        "p_exercises": exercises
    }).execute()

def getUserWorkouts(userEmail, userName):
    workouts = supabase.rpc("get_user_workouts", {
        "p_username":userName,
        "p_useremail":userEmail,
    }).execute()
    workouts = workouts.data
    for workout in workouts:
        workout["date"] = str(workout["date"])[:10] #Clean up date formatting
    return workouts

def getLastLogin(userEmail, userName):
    date = supabase.rpc("get_last_login", {
        "p_useremail":userEmail,
        "p_username":userName
    }).execute()
    return str(date.data)[:10] #Clean up date formatting
def updateLastLogin(userEmail, userName):
    supabase.rpc("update_user_login", {
        "p_useremail":userEmail,
        "p_username":userName
    }).execute()
    
    