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

#def updateWorkoutPlan(userEmail, userName, workouts):
    