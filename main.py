from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import AsyncGenerator, List, Tuple
import networkx as nx
import osmnx as ox
import time

from routing.load_data import load_flooded_areas
from routing.models import RouteRequest, Route, DirectionsResponse
from routing.global_variables import (
    calculate_duration,
    calculate_distance,
)
from routing.route_system.safest_route_computation import find_safest_route
from routing.direction_system.directions import get_directions


# Load the flooded areas on startup
@asynccontextmanager
async def startup_event(app: FastAPI) -> AsyncGenerator[None, None]:
    await load_flooded_areas()
    yield


# Initialize the FastAPI app
app = FastAPI(lifespan=startup_event)


@app.post("/directions")
async def directions(route_request: RouteRequest) -> DirectionsResponse:
    # Parse the start and end coordinates
    start_lng, start_lat = map(float, route_request.start.split(","))
    end_lng, end_lat = map(float, route_request.end.split(","))

    start_time = time.time()

    # Find the safest route between the start and end coordinates
    safest_route, route_coordinates, G, path, route = await find_safest_route(
        (start_lat, start_lng),
        (end_lat, end_lng),
    )

    # Get the route information
    route_info = get_directions(G, path, route)

    end_time = time.time()

    print(f"Time taken to find the safest route: {end_time - start_time:.2f} seconds")

    if safest_route:
        # Calculate the total distance and duration of the route
        total_distance_km = calculate_distance(safest_route)
        duration_minutes = calculate_duration(total_distance_km * 1000)

        # Return the directions response
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
        # Return an error message if no safe route is found
        raise HTTPException(
            status_code=404,
            detail="No safe route found. All possible routes pass through flooded areas.",
        )
