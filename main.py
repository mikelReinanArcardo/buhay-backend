from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from typing import AsyncGenerator
import json

from routing.load_data import load_flooded_areas
from tsp_endpoint import main_tsp
from tests.naive_tsp import naive_tsp  # For testing

from database_endpoints import convert_coordinates, login_endpoint

from routing.route_directions import directions
from models import DirectionsRequest
from routing.cache_database import (
    connect_to_database,
    close_database_connection,
    route_info,
    update_rescued_boolean,
)
from models import Point, RouteInfo, UpdateRescued
from qc_coordinates import check_point_in_polygon
from own_websocket import own_socket


# Load the flooded areas on startup
@asynccontextmanager
async def startup_event(app: FastAPI) -> AsyncGenerator[None, None]:
    await load_flooded_areas()
    await connect_to_database()
    await own_socket.start_db_listener()
    yield
    await close_database_connection()


# Initialize the FastAPI app
app = FastAPI(lifespan=startup_event)

# Include router for tsp endpoint
app.include_router(main_tsp.router)
app.include_router(naive_tsp.router)  # For testing
app.include_router(own_socket.router)
app.include_router(login_endpoint.router)
app.include_router(convert_coordinates.router)


# app.include_router(route_directions.router)
@app.post("/directions", status_code=status.HTTP_200_OK)
async def call_directions(directionRequest: DirectionsRequest):
    return await directions(directionRequest)


@app.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    return {"message": "pong"}


@app.post("/checkCoordinates", status_code=status.HTTP_200_OK)
async def checkCoordinates(point: Point):
    if await check_point_in_polygon(point.coordinates):
        return {"message": "true"}
    return {"message": "false"}


@app.get("/test", status_code=status.HTTP_200_OK)
async def test():
    with open("sample_data.json", "r") as f:
        json_data = json.load(f)
    return json_data


@app.post("/get_route_info", status_code=status.HTTP_200_OK)
async def get_route_info(route_id: RouteInfo):
    data = await route_info(route_id.route_id)
    return {"payload": data}


@app.post("/update_rescued", status_code=status.HTTP_200_OK)
async def update_rescued(request_id: UpdateRescued):
    await update_rescued_boolean(request_id.request_id)
    return {"message": "done"}
