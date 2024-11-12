import aiofiles
import os
from shapely.geometry import Polygon, Point
from rtree import index
import json
from global_variables import (
    set_flood_index,
    set_flooded_areas,
)


async def load_flooded_areas():
    dir = os.listdir("./flood_data")
    flooded_areas = {}
    flood_index = {}
    for file in dir:
        async with aiofiles.open(f"./flood_data/{file}") as f:
            data = await f.read()
            areas = [
                Polygon([(lat, lng) for lng, lat in area[0]])
                for area in json.loads(data)["features"][0]["geometry"]["coordinates"]
            ]

            # Create R-tree index
            idx = index.Index()
            for i, area in enumerate(areas):
                idx.insert(i, area.bounds)
            flooded_areas[file] = areas
            flood_index[file] = idx
    set_flooded_areas(flooded_areas)  # Use the setter function
    set_flood_index(flood_index)  # Use the setter function
