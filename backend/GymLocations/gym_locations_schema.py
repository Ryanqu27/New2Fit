from pydantic import BaseModel

class GymDTO(BaseModel):
    URL: str
    latitude: float
    longitude: float
    city: str
    state: str
    brand: str