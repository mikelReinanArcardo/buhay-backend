import asyncio
from typing import Tuple, List
import networkx as nx
from rtree import index
from shapely.geometry import Point
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import osmnx as ox

from global_variables import (
    get_flood_index,
    get_flooded_areas,
    get_road_network_cache,
    set_road_network_cache,
)
from general_computations import calculate_geodesic_distance


@lru_cache(maxsize=10000)
def calculate_flood_risk(point: Tuple[float, float]) -> float:
    flood_index = get_flood_index()
    flooded_areas = get_flooded_areas()

    point_geom = Point(point)
    nearby_areas = list(flood_index.intersection(point_geom.bounds))

    if not nearby_areas:
        return 0.0

    distances = [point_geom.distance(flooded_areas[i]) for i in nearby_areas]
    closest_distance = min(distances)

    if closest_distance == 0:
        return 1.0

    max_effect_distance = 0.01  # About 1km in degrees
    return max(0, 1 - (closest_distance / max_effect_distance))


async def compute_flood_risk(graph: nx.Graph, nodes: List[int]) -> None:
    loop = asyncio.get_event_loop()
    chunk_size = 1000  # Process nodes in chunks to avoid memory issues

    for i in range(0, len(nodes), chunk_size):
        chunk = nodes[i : i + chunk_size]
        flood_risks = await loop.run_in_executor(
            ThreadPoolExecutor(),
            lambda: {
                u: calculate_flood_risk((graph.nodes[u]["y"], graph.nodes[u]["x"]))
                for u in chunk
            },
        )

        for u, risk in flood_risks.items():
            graph.nodes[u]["flood_risk"] = risk


async def get_road_network(
    start: Tuple[float, float], end: Tuple[float, float]
) -> nx.Graph:
    road_network_cache = get_road_network_cache()
    key = (start, end)

    if key in road_network_cache:
        return road_network_cache[key]

    distance = calculate_geodesic_distance(start, end)
    buffer = min(0.015, distance * 0.1)

    north = max(start[0], end[0]) + buffer
    south = min(start[0], end[0]) - buffer
    east = max(start[1], end[1]) + buffer
    west = min(start[1], end[1]) - buffer

    bbox = (north, south, east, west)
    G = ox.graph_from_bbox(north, south, east, west, network_type="walk", simplify=True)

    await compute_flood_risk(G, list(G.nodes))

    set_road_network_cache(G)

    return G
