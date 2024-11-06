# Placeholder for flooded areas and R-tree index
FLOODED_AREAS = []
FLOOD_INDEX = None

# Placeholder for road network cache
ROAD_NETWORK_CACHE = {}

# Define flood exposure thresholds
HIGH_EXPOSURE_THRESHOLD = 0.5  # 500 meters of flood exposure
MEDIUM_EXPOSURE_THRESHOLD = 0.1  # 100 meters of flood exposure


def get_flood_index():
    global FLOOD_INDEX
    return FLOOD_INDEX


def set_flood_index(index):
    global FLOOD_INDEX
    FLOOD_INDEX = index


def get_flooded_areas():
    global FLOODED_AREAS
    return FLOODED_AREAS


def set_flooded_areas(areas):
    global FLOODED_AREAS
    FLOODED_AREAS = areas


def get_road_network_cache():
    global ROAD_NETWORK_CACHE
    return ROAD_NETWORK_CACHE


def set_road_network_cache(cache):
    global ROAD_NETWORK_CACHE
    ROAD_NETWORK_CACHE = cache
