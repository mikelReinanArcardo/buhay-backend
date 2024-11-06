"""
BUGS
- For testing
- Transfer computing directions to a different file or endpoint.
"""

from fastapi import FastAPI, HTTPException
from typing import List, Tuple
import networkx as nx
import osmnx as ox
import time

from load_data import load_flooded_areas
from models import RouteRequest, RouteInfo, Route, DirectionsResponse
from general_computations import (
    calculate_geodesic_distance,
    weight_function,
    calculate_duration,
    get_street_name,
    calculate_distance,
    get_cardinal_direction,
    get_turn_direction,
)
from flood_computation import get_road_network

# Initialize the FastAPI app
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await load_flooded_areas()


@app.post("/directions")
async def directions(route_request: RouteRequest):
    start_lng, start_lat = map(float, route_request.start.split(","))
    end_lng, end_lat = map(float, route_request.end.split(","))

    start_time = time.time()

    safest_route, route_coordinates, route_info = await find_safest_route(
        (start_lat, start_lng), (end_lat, end_lng)
    )

    elapsed_time = time.time() - start_time
    print(f"Routing completed in {elapsed_time:.2f} seconds.")

    if safest_route:
        total_distance_km = calculate_distance(safest_route)
        duration_minutes = calculate_duration(total_distance_km * 1000)
        return DirectionsResponse(
            route=Route(
                duration=duration_minutes,
                distanceKm=total_distance_km,
                coordinates=route_coordinates,
                routeInfo=route_info,
            ),
            message=f"Safe route found. Total distance: {total_distance_km:.2f}km. Estimated duration: {duration_minutes:.0f} minutes.",
        )
    else:
        raise HTTPException(
            status_code=404,
            detail="No safe route found. All possible routes pass through flooded areas.",
        )


async def find_safest_route(
    start: Tuple[float, float], end: Tuple[float, float]
) -> Tuple[List[Tuple[float, float]], List[List[float]], List[RouteInfo]]:
    G = await get_road_network(start, end)
    start_node = ox.nearest_nodes(G, start[1], start[0])
    end_node = ox.nearest_nodes(G, end[1], end[0])

    try:
        path = nx.astar_path(
            G,
            start_node,
            end_node,
            heuristic=lambda u, v: calculate_geodesic_distance(
                (G.nodes[u]["y"], G.nodes[u]["x"]), (G.nodes[v]["y"], G.nodes[v]["x"])
            ),
            weight=weight_function,
        )

        route = [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in path]

        coordinates = [[coord[1], coord[0]] for coord in route]  # [lng, lat]
        route_info = []
        cumulative_distance = 0
        current_street = get_street_name(G, path[0], path[1])

        for i in range(1, len(path)):
            new_street = get_street_name(G, path[i - 1], path[i])
            segment_distance = calculate_geodesic_distance(route[i - 1], route[i])
            cumulative_distance += segment_distance

            if new_street != current_street or i == len(path) - 1:
                if i == 1:  # Starting point
                    direction = get_cardinal_direction(route[0], route[1])
                    instruction = f"Walk {direction} on {current_street}."
                elif i == len(path) - 1:  # Ending point
                    instruction = "You have arrived at your destination."
                else:
                    turn = get_turn_direction(
                        route[0], route[i - 2], route[i - 1], route[i]
                    )
                    instruction = f"{turn} onto {new_street}."

                route_info.append(
                    RouteInfo(
                        instruction=instruction,
                        distance=round(cumulative_distance, 2),
                    )
                )

                current_street = new_street
                cumulative_distance = 0

        return route, coordinates, route_info

    except nx.NetworkXNoPath:
        return None, None, None
