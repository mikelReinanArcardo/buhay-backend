from fastapi import APIRouter, HTTPException, status
from fastapi.params import Body

from models import Point
from tsp_endpoint.auxiliary_functions import create_graph, append_starting_node, node_to_json_parser
import networkx as nx
from typing import List

router = APIRouter()

@router.get("/tsp", status_code = status.HTTP_200_OK)
async def tsp(points: List[Point]) -> List[Point]:
    try:
        # Convert input points into a complete, weighted, directed graph, in which the weights of the edges are the haversine distance between the adjacent vertices.
        G: nx.Graph = create_graph(points)

        # Search for the shortest acyclic hamiltonian path connecting nodes 1 to n-1.
        tsp_route = nx.approximation.traveling_salesman_problem(
            G = G,
            nodes = list(G.nodes)[1:],
            weight = "weight",
            cycle = False,
        )
        
        # Connect the starting node (0) to the closest end of the shortest hamiltonian path.
        tsp_route = append_starting_node(G, tsp_route)

        return node_to_json_parser(G, tsp_route)
    
    except nx.NetworkXError as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "If G is a directed graph it has to be strongly connected or the complete version cannot be generated."
        )

    except ValueError as e:
        # Handle specific exceptions with a 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request.",
        )

    except HTTPException as e:
        # Re-raise HTTPExceptions
        raise e

    except Exception as e:
        # Handle unexpected server errors with a 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )