import numpy as np

MINUTE = 60
HOUR = MINUTE*60
DAY = HOUR*24
WEEK = DAY*7
MONTH = WEEK*4
class BeeSwarmConfig:
    # TODO: back up with beta probability theory
    PERCEPTION =  100   # Perception (no. of samples parameter) for generating alpha, beta (Beta distribution) in hive inspection
    P_NECTAR_INSPECTION = 0.01 # (probability / s) | probability to assess hive nectar level
    P_NECTAR_COMMUNICATION = 0.02 # (probability / s) | probability to communicate hive nectar level to other bees
    EXPLORING_INCENTIVE = 0.1  # Lambda parameter in exponential distribution going into exploration state

    BEE_SWARM_SIZE = 100                            # (count) | Number of bees represented by a single BeeSwarm agent
    CARRYING_CAPACITY = 30e-6 * BEE_SWARM_SIZE      # (in kg) = 30mg per bee | Amount of resources a bee swarm can carry
    SCENT_SCALE = 2.5                               # (scale) = 50% more focused on following scent
    FIELD_OF_VIEW = 10                              # (in m) TODO: calibrate further using real data
    STARVATION_SPEED = 1/DAY                        # (in rate/s)
    MAX_AGE = np.inf                                # (in s) = not used
    P_DEATH_BY_STORM = 1/(10*MINUTE)                # (probability / s) = on average within 10 minute TODO: calibrate further
    SPEED = 3.5                                     # (in m/s) = 12.6km/h
    DANCING_TIME = MINUTE                           # (in s) TODO: calibrate further
    P_FOLLOW_WIGGLE_DANCE = 0.5                     # (probability) TODO: calibrate further
    P_ABORT = 1/HOUR                                # (probability) TODO: calibrate further
    STORM_ABORT_FACTOR = 100                        # (scale) = 100 times more likely to abort during storm TODO: calibrate further
    FEED_STORAGE = 0.01e-3 * BEE_SWARM_SIZE            # (in kg) = 0.01g per bee

class HiveConfig:
    MAX_NECTAR_CAPACITY = 20            # (in kg) | NOTE: Quantity approximately needed to survive winter, given in "Wisdom of the Hive" book.
    DEFAULT_RADIUS = 0.5                # (in m)
    DEFAULT_NECTAR = 0.5                # (in kg)
    INIT_YOUNG_BEES = 0                 # (count) = not used
    FEED_RATE: float = 1/MINUTE         # (rate/s)
    P_NEW_FORAGER: float = 1/(10*DAY)   # (probability / s) = on average within 10 days

class ResourceConfig:
    DEFAULT_QUANTITY = 1                # (in kg)
    DEFAULT_RADIUS = 100.0              # (in m)
    NECTAR_PRODUCTION_RATE = 0          # 2e-7 * np.pi * DEFAULT_RADIUS**2 / (60*60*24) # (in kg/s) | stems from this formula for flower nectar production: growth = 0.2 mg / (m^2 * day) from paper (https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2745.13598)
    DEFAULT_PERSISTENT = False

class VisualConfig:
    RENDER_SIZE = 600
    HIVE_RADIUS = 0.03*RENDER_SIZE
    BEE_RADIUS = 0.002*RENDER_SIZE

class ModelConfig:
    SIZE = 10_000                       # (in m) = 10km x 10km
    DT = MINUTE                         # (in s) = 1 minute
    P_STORM_DEFAULT = 1/(10*DAY)        # (probability / s) = on average every 10 days
    STORM_DURATION_DEFAULT = DAY        # (in s)
    N_BEESWARMS = 500                   # (count)
    N_HIVES = 1                         # (count)
    ABUNDANCE_RATIO = 0.1                 # (radio) how many times the max hive capacity in resources should be generated?
    N_RESOURCE_SITES = int((ABUNDANCE_RATIO*HiveConfig.MAX_NECTAR_CAPACITY)/ResourceConfig.DEFAULT_QUANTITY) # (count)