import csv
import os
from .gym_locations_schema import GymDTO

def get_all_gyms_dto():
    gyms = []
    csv_file_path = os.path.join(os.path.dirname(__file__), 'Gyms.csv')
    
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            gym_dto = GymDTO(
                URL=row['URL'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                city=row['city'],
                state=row['state'],
                brand=row['brand']
            )
            gyms.append(gym_dto)
            
    return gyms
