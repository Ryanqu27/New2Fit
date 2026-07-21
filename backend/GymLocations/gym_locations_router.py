from fastapi import APIRouter, Request
from .gym_locations_schema import GymDTO
from .gym_locations import get_all_gyms_dto
from limiter import limiter

router = APIRouter(prefix="/api/gymLocations", tags=["GymLocations"])


@router.get("/gyms", response_model=list[GymDTO])
@limiter.limit("20/minute")
def get_gyms(request: Request):
    return get_all_gyms_dto()
    