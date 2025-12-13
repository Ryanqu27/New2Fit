import requests
import pandas as pd

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

anytimeFitnessResponse = requests.get("https://react.anytimefitness.com/api/locations/?country=usa")
anytimeFitnessJson = anytimeFitnessResponse.json()
anytimeFitnessGyms = anytimeFitnessJson.get("items")
for gym in anytimeFitnessGyms:
    address = gym.get("address", {})

    city = address.get("city")
    state = address.get("state")
    location_number = gym.get("location_number")

    if not (city and state and location_number):
        continue  # skip malformed entries

    city_slug = city.lower().replace(" ", "-")
    state_slug = state.lower().replace(" ", "-")

    url = f"https://www.anytimefitness.com/locations/{city_slug}-{state_slug}-{location_number}"

    gymDataFrame.loc[len(gymDataFrame)] = [
        url,
        gym.get("latitude"),
        gym.get("longitude"),
        city,
        state,
        "Anytime Fitness"
    ]

gymDataFrame.to_csv("GymLocations/Gyms.csv")
