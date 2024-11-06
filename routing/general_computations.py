from typing import Tuple
from functools import lru_cache
import networkx as nx
from typing import List
from global_variables import HIGH_EXPOSURE_THRESHOLD, MEDIUM_EXPOSURE_THRESHOLD
from geopy import distance
import osmnx as ox


@lru_cache(maxsize=1000)
def calculate_geodesic_distance(
    point1: Tuple[float, float], point2: Tuple[float, float]
) -> float:
    return distance.distance(point1, point2).km


def calculate_distance(route: List[Tuple[float, float]]) -> float:
    return sum(
        calculate_geodesic_distance(route[i], route[i + 1])
        for i in range(len(route) - 1)
    )


def weight_function(u, v, d):
    length = d[0].get("length", 1)
    flood_risk = d[0].get("flood_risk", 0)

    flood_exposure_length = length * flood_risk
    if flood_exposure_length > HIGH_EXPOSURE_THRESHOLD:
        return length * 10
    elif flood_exposure_length > MEDIUM_EXPOSURE_THRESHOLD:
        return length * 5
    elif flood_risk > 0:
        return length * 2
    return length


def calculate_duration(distance_meters: int, average_speed: float = 5.0) -> float:
    """Calculate the estimated duration in minutes based on distance and average walking speed."""
    return (distance_meters / 1000) / average_speed * 60


def get_street_name(G: nx.Graph, u: int, v: int) -> str:
    """Get the street name for the edge between two nodes."""
    edge_data = G.get_edge_data(u, v, 0)
    if "name" in edge_data:
        return edge_data["name"]
    return "Unnamed Street"


def get_cardinal_direction(start: Tuple[float, float], end: Tuple[float, float]) -> str:
    angle = ox.bearing.calculate_bearing(start[0], start[1], end[0], end[1])
    directions = [
        "north",
        "northeast",
        "east",
        "southeast",
        "south",
        "southwest",
        "west",
        "northwest",
    ]
    index = round(angle / 45) % 8
    return directions[index]


def get_turn_direction(
    start: Tuple[float, float],
    a: Tuple[float, float],
    b: Tuple[float, float],
    c: Tuple[float, float],
) -> str:
    # Calculate the initial bearing from the start point
    initial_bearing = ox.bearing.calculate_bearing(start[0], start[1], a[0], a[1])

    # Calculate the bearings for the two segments
    bearing1 = ox.bearing.calculate_bearing(a[0], a[1], b[0], b[1])
    bearing2 = ox.bearing.calculate_bearing(b[0], b[1], c[0], c[1])

    # Normalize the bearings relative to the initial bearing
    angle1 = (bearing1 - initial_bearing + 360) % 360
    angle2 = (bearing2 - initial_bearing + 360) % 360

    # Calculate the turn angle
    turn_angle = (angle2 - angle1 + 360) % 360

    if turn_angle < 10 or turn_angle > 350:
        return "Continue straight"
    elif 10 <= turn_angle < 170:
        return "Turn right"
    elif 190 <= turn_angle < 350:
        return "Turn left"
    else:
        return "Make a U-turn"
