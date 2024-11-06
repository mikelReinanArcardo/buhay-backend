import aiofiles
from shapely.geometry import Polygon, Point
from rtree import index
import json
from global_variables import (
    set_flood_index,
    set_flooded_areas,
)


async def load_flooded_areas():
    async with aiofiles.open("./coordinates3.json") as f:
        data = await f.read()
        areas = [
            Polygon([(lat, lng) for lng, lat in area[0]])
            for area in json.loads(data)["features"][0]["geometry"]["coordinates"]
        ]

        # Create R-tree index
        idx = index.Index()
        for i, area in enumerate(areas):
            idx.insert(i, area.bounds)

        set_flooded_areas(areas)  # Use the setter function
        set_flood_index(idx)  # Use the setter function
