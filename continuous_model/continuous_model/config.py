class BeeConfig:
    FIELD_OF_VIEW = 20              # 20 (in m) TODO: calibrate further using real data
    STARVATION_SPEED = 1/(60*60*24) # within 1 day (in rate/s)
    MAX_AGE = (60*60*24*7*6)        # within 6 weeks (in s)
    P_DEATH_BY_STORM = 1/(60*60)    # on average within 1 hour (probability) TODO: calibrate further
    SPEED = 5                       # 5 (in m/s) 
    PERCEIVE_AS_LOW_FOOD = 2        # 2 (in kg) TODO: calibrate further
    DANCING_TIME = 60               # 1 minute (in s) TODO: calibrate further
    P_FOLLOW_WIGGLE_DANCE = 1       # 100% (probability) TODO: calibrate further
    P_ABORT_EXPLORING = 1/(60*60)   # on average within 1 hour (probability) TODO: calibrate further
    P_ABORT_FOLLOWING = 1/(60*60)   # on average within 1 hour (probability) TODO: calibrate further
    STORM_ABORT_FACTOR = 10         # 10 times more likely to abort during storm TODO: calibrate further
    CARRYING_CAPACITY = 0.001       # 1g (in kg) TODO: calibrate further
    GATHERING_RATE = 0.0001         # 0.1g/s (kg/s) TODO: calibrate further

class HiveConfig:
    RADIUS = 20  # for drawing in Javascript server visualization
    DEFAULT_RADIUS = 10.0
    DEFAULT_NECTAR = 0.5
    DEFAULT_WATER = 0.5
    DEFAULT_POLLEN = 0.5
    DEFAULT_YOUNG_BEES = 0