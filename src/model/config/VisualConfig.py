from .HiveConfig import HiveConfig as HC
from .ResourceConfig import ResourceConfig as RC

from ..agents.Resource import Resource

from ..util.BeeState import BeeState

from enum import Enum

class VisualConfig:

    # Activity dependent color of bee in the visualization
    BEE_COLORS = {
        BeeState.RESTING : "#fc0303", # red
        BeeState.RETURNING: "#3bf55a", # green
        BeeState.EXPLORING : "#0af5f1", # blue
        BeeState.CARRYING : "#59a2c2", # light blue
        BeeState.DANCING : "#ff52df", # pink
        BeeState.FOLLOWING : "#0a54f5" # dark blue
    }

    # Color of hive in the visualization
    HIVE_COLOR = "#e6cb02" # deep yellow

    # Color of resource in the visualization (white if quantity reached 0)
    RESOURCE_COLOR = lambda resource : "#47ad1f" if resource.quantity > 0 else "#ffffff" # deep green or white if empty

    # Grid size for JS server visualization
    RENDER_SCALE = 3

    # Hive radius size in JS server visualization
    HIVE_RADIUS = HC.RADIUS * RENDER_SCALE

    # Bee agent radius size in JS server visualization
    BEE_RADIUS = 0.4 * RENDER_SCALE

    # Resource agent radius size in JS server visualization
    RESOURCE_RADIUS = RC.RADIUS * RENDER_SCALE

    # Default value of storm probability in JS server visualization
    P_STORM_DEFAULT = 0.005

    # Default value of storm duration in JS server visualization
    STORM_DURATION_DEFAULT = 20

    # Default number of resources in JS server visualization
    N_RESOURCES_DEFAULT = 2

    # Default distance of all resources to the hive in JS server visualization
    RESOURCE_DISTANCE_DEFAULT = 50
