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

    # Make this dynamic based on the file_name
    flood_weights = {
        "coordinates1.json": 1,
        "coordinates2.json": 2,
        "coordinates3.json": 3,
    }

    point_geom = Point(point)
    nearby_areas = {}

    for key, idx in flood_index.items():
        nearby_areas[key] = list(idx.intersection(point_geom.bounds))

    if all(not areas for areas in nearby_areas.values()):
        return 0.0

    distances = {}
    for key, areas in nearby_areas.items():
        distances[key] = [point_geom.distance(flooded_areas[key][i]) for i in areas]

    closest_distance = {}
    for key, dists in distances.items():
        if dists:
            closest_distance[key] = min(dists)

    risk = 0.0
    max_effect_distance = 0.01  # About 1km in degrees
    for key, distance in closest_distance.items():
        level_risk = flood_weights.get(key, 0) - (distance / max_effect_distance)
        risk = max(risk, level_risk)

    return risk


async def compute_flood_risk(graph: nx.Graph, nodes: List[int]) -> None:
    loop = asyncio.get_event_loop()
    chunk_size = 1000

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


def assign_edge_flood_risk(G: nx.Graph) -> None:
    for u, v, d in G.edges(data=True):
        u_risk = G.nodes[u].get("flood_risk", 0)
        v_risk = G.nodes[v].get("flood_risk", 0)
        d["flood_risk"] = (u_risk + v_risk) / 2


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

    # Assign flood risk to edges based on node flood risks
    assign_edge_flood_risk(G)

    set_road_network_cache(G)

    return G
