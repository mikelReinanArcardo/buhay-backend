import networkx as nx
from osmnx.distance import great_circle
from models import Point
from typing import List

def create_graph(points: List[Point]) -> nx.Graph: 
    n = len(points) 
    G = nx.Graph()

    # Add points[i] as the ith node of the graph
    for i in range(n):
        G.add_node(
            i, 
            location_name = points[i].location_name, 
            lat = points[i].coordinates[0], 
            lng = points[i].coordinates[1]
        )
    
    # Add edge(i,j) for each possible i,j combination such that its weight is the haversine distance between Point i and Point j
    for i in range(n):
        lat_i, lng_i = points[i].coordinates
        for j in range(i+1, n):
            lat_j, lng_j = points[j].coordinates
            haversine_distance = great_circle(lat_i, lng_i, lat_j, lng_j)
            G.add_edge(
                i, j,
                weight = haversine_distance
            )
    
    return G

def append_starting_node(G: nx.Graph, tsp_route: List[int]) -> List[int]:
    # Compare the haversine distance between the starting node and each end of the hamiltonian path containing nodes 1 to n-1.
    # Put starting node 0 next to the hamiltonian end node that is closer.
    # Reverse the output list if the starting node was put on the right end of the list.

    starting_node = 0
    lat_0, lng_0 = G.nodes[starting_node]['lat'], G.nodes[starting_node]['lng']
    left_end = tsp_route[0]
    lat_left, lng_left = G.nodes[left_end]['lat'], G.nodes[left_end]['lng']
    right_end = tsp_route[-1]
    lat_right, lng_right = G.nodes[right_end]['lat'], G.nodes[right_end]['lng']

    if great_circle(lat_0, lng_0, lat_left, lng_left) < great_circle(lat_0, lng_0, lat_right, lng_right): 
        complete_tsp: List[int] = [0] + tsp_route
    else:
        complete_tsp: List[int] = [0] + tsp_route[::-1]

    return complete_tsp

def node_to_json_parser(G: nx.Graph, nodes: List[int]) -> List[Point]:
    ret: List[Point] = []
    for node in nodes:
        ret.append({
            "location_name": G.nodes[node]["location_name"],
            "coordinates": [G.nodes[node]["lat"], G.nodes[node]["lng"]]
        })
    return ret