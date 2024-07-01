import numpy as np

class BeeConfig:
    # Perception (no. of samples parameter) for generating alpha, beta (Beta distribution) in hive inspection
    PERCEPTION =  10                # TODO: back up with beta probability theory
    P_NECTAR_INSPECTION = 0.01 # (probability / s) | probability to assess hive nectar level
    P_NECTAR_COMMUNICATION = 0.02 # (probability / s) | probability to communicate hive nectar level to other bees

    # Inverse of lambda parameter in exponential distribution going into exploration state
    EXPLORING_INCENTIVE = 0.5

    # Number of bees represented by a single Bee agent
    BEES_IN_SWARM = 100
    
    # Quantity given in "Wisdom of the Hive" book
    CARRYING_CAPACITY = 30e-3       # [grams] = 30[mg] TODO: Adjust to actual number of Bee agents we use (1 agent = multiple bees)
    SCENT_SCALE = 0.5               # 50% more focused on following scent
    FIELD_OF_VIEW = 10              # 20 (in m) TODO: calibrate further using real data
    STARVATION_SPEED = 1/(60*60*24) # 1/(60*60*24) # within 1 day (in rate/s)
    MAX_AGE = (60*60*24*7*6)        # within 6 weeks (in s)
    P_DEATH_BY_STORM = 1/(60*10)    # on average within 10 minute (probability) TODO: calibrate further
    SPEED = 5                       # 5 (in m/s) 
    DANCING_TIME = 60               # 1 minute (in s) TODO: calibrate further
    P_FOLLOW_WIGGLE_DANCE = 1       # 100% (probability) TODO: calibrate further
    P_ABORT_EXPLORING = 1/(60*60)   # on average within 1 hour (probability) TODO: calibrate further
    P_ABORT_FOLLOWING = 1/(60*60)   # on average within 1 hour (probability) TODO: calibrate further
    STORM_ABORT_FACTOR = 1000       # 1000 times more likely to abort during storm TODO: calibrate further
    GATHERING_RATE = 0.0001         # 0.1g/s (kg/s) TODO: calibrate further

class HiveConfig:
    MAX_NECTAR_CAPACITY = 20e3      # [grams] = 20[kg]. Quantity approximately needed to survive winter, given in "Wisdom of the Hive" book.
    DEFAULT_RADIUS = 0.5 # (in m) = 10m
    DEFAULT_NECTAR = 0.0 # (in kg) = 0g
    DEFAULT_WATER = 0.5 # TODO: not used
    DEFAULT_POLLEN = 0.5 # TODO: not used
    DEFAULT_YOUNG_BEES = 0 # (count)
    DEFAULT_FEED_RATE: float = 1/60  # (rate / s) = within 1 minute

class ModelConfig:
    SIZE = 10_000   # (in m) = 10km x 10km
    DT = 20         # (in s) = 1 minute
    P_STORM_DEFAULT = 1/(60*24*24*10)  # (probability / s) = on average every 10 days
    STORM_DURATION_DEFAULT = 60*60*24   # (in s) = 1 day
    N_BEES = 1_000 # (count)
    N_HIVES = 1 # (count)
    N_RESOURCE_SITES = 3 # (count) # TODO: calibrate i.e. scale to space size

class ResourceConfig:
    DEFAULT_QUANTITY = 0.1 # (in kg) = 100g per site
    DEFAULT_RADIUS = 200.0 # (in m) = 200m
    NECTAR_PRODUCTION_RATE = 0 # 2e-7 * np.pi * DEFAULT_RADIUS**2 / (60*60*24) # (in kg/s) | stems from this formula for flower nectar production: growth = 0.2 mg / (m^2 * day) from paper (https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2745.13598)
    DEFAULT_PERSISTENT = False

class VisualConfig:
    RENDER_SIZE = 600
    HIVE_RADIUS = 0.03*RENDER_SIZE
    BEE_RADIUS = 0.002*RENDER_SIZE
