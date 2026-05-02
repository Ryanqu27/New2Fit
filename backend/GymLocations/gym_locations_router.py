from fastapi import APIRouter
from .gym_locations_schema import GymDTO
from .gym_locations import get_all_gyms_dto

router = APIRouter(prefix="/api/gymLocations", tags=["GymLocations"])


@router.get("/gyms", response_model=list[GymDTO])
def get_gyms():
    return get_all_gyms_dto()
    