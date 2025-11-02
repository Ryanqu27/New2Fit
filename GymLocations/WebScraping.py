import requests
import pandas as pd
import csv

# Using the "slug" location after https://www.crunch.com/locations/_____ will retrieve location website
crunchResponse = requests.get("https://www.crunch.com/load-clubs")
crunchJson = crunchResponse.json()
crunchGyms = crunchJson.get("clubs")
gymDataFrame = pd.DataFrame({"URL": [], "latitude": [], "longitude": [], "city": [], "state": [], "brand": []})
for gym in crunchGyms:
    gymDataFrame.loc[len(gymDataFrame)] = [
        "https://www.crunch.com/locations/" + gym.get("slug"), 
        gym.get("latitude"), 
        gym.get("longitude"), 
        gym["address"].get("city"), 
        gym["address"].get("state"),
        "Crunch"
    ]

gymDataFrame.to_csv("GymLocations/CrunchGyms.csv")
