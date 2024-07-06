from enum import Enum

class BeeState(Enum):
    RESTING = "resting"
    RETURNING = "returning"
    EXPLORING = "exploring"
    CARRYING = "carrying"
    DANCING = "dancing"
    FOLLOWING = "following"