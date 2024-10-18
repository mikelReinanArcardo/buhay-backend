from pydantic import BaseModel
from typing import List, Tuple, Dict


class RouteRequest(BaseModel):
    start: str
    end: str


class RouteInfo(BaseModel):
    instruction: str
    distance: float  # Distance in kilometers


class Route(BaseModel):
    duration: float
    distanceKm: float
    coordinates: List[List[float]]
    routeInfo: List[RouteInfo]


class DirectionsResponse(BaseModel):
    route: Route
    message: str = None
