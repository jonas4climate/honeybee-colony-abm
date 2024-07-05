from enum import Enum

class SpaceSetup(Enum):
    RANDOM = 'random' # Resources are placed randomly in the space
    FIXED_DISTANCE_FROM_HIVE = 'fixed distance from hive' # Resources are placed at a fixed distance from the hive (Experiment 1)