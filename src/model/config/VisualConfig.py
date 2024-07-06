from .HiveConfig import HiveConfig as HC
from .ResourceConfig import ResourceConfig as RC

from enum import Enum

class VisualMode(Enum):
    CLASSIC = 0
    SERVER = 1

class VisualConfig:

    # Default number of resources in JS server visualization
    N_RESOURCES_DEFAULT = 1

    # Default distance of all resources to the hive in JS server visualization
    RESOURCE_DISTANCE_DEFAULT = 20

    # Grid size for JS server visualization
    RENDER_SCALE = 3

    # Hive radius size in JS server visualization
    HIVE_RADIUS = HC.RADIUS * RENDER_SCALE

    # Bee agent radius size in JS server visualization
    BEE_RADIUS = 0.4 * RENDER_SCALE

    # Resource agent radius size in JS server visualization
    RESOURCE_RADIUS = RC.RADIUS * RENDER_SCALE
