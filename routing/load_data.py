import aiofiles
import os
from shapely.geometry import Polygon, Point
from rtree import index
import json
from routing.global_variables import (
    set_flood_index,
    set_flooded_areas,
)


async def load_flooded_areas():
    # Get the list of files in the flood_data directory
    # TODO: flood_data will be stored in a cloud storage, so this will be replaced with a cloud storage API
    dir = "./routing/flood_data"
    files = os.listdir(dir)

    # Placeholder for the flooded areas and R-tree index
    flooded_areas = {}
    flood_index = {}

    # Load the flooded areas
    for file in files:
        # Read the file
        async with aiofiles.open(f"{dir}/{file}") as f:
            data = await f.read()

            # Parse the data
            areas = [
                Polygon([(lat, lng) for lng, lat in area[0]])
                for area in json.loads(data)["features"][0]["geometry"]["coordinates"]
            ]

            # Create R-tree index
            idx = index.Index()
            for i, area in enumerate(areas):
                idx.insert(i, area.bounds)

            # Store the data as a key-value pair
            flooded_areas[file] = areas
            flood_index[file] = idx

    # Set the global variables
    set_flooded_areas(flooded_areas)
    set_flood_index(flood_index)
