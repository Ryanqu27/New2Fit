from datetime import datetime, date
import DataBaseManaging.SupaBase as db
today = date.today().isoformat()
print(today)
print(db.getLastLogin("ryanqu27@gmail.com", "Ryan Qu"))
