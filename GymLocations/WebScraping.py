import requests
import pandas as pd
import csv

# Using the "slug" location after https://www.crunch.com/locations/_____ will retrieve location website
crunchResponse = requests.get("https://www.crunch.com/load-clubs")
crunchJson = crunchResponse.json()
crunchGyms = crunchJson.get("clubs")
crunchGymDataFrame = pd.DataFrame({"URL": [], "latitude": [], "longitude": [], "city": [], "state": []})
for gym in crunchGyms:
    slug = gym.get("slug")
    latitude = gym.get("latitude")
    longitude = gym.get("longitude")
    city = gym["address"].get("city")
    state = gym["address"].get("state")
    crunchGymDataFrame.loc[len(crunchGymDataFrame)] = ["https://www.crunch.com/locations/" + slug, latitude, longitude, city, state]

crunchGymDataFrame.to_csv("GymLocations/CrunchGyms.csv")