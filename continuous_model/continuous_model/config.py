import numpy as np

# Unit utility
MINUTE = 60
HOUR = MINUTE*60
DAY = HOUR*24
WEEK = DAY*7
MONTH = WEEK*4
GRAMM = 1e-3
MILLIGRAMM = 1e-6

class BeeSwarmConfig:
    def __init__(self, **kwargs):
        # TODO: back up with beta probability theory
        self.perception = kwargs.get('perception', 100)                             # Perception (no. of samples parameter) for generating alpha, beta (Beta distribution) in hive inspection
        self.p_nectar_inspection = kwargs.get('p_nectar_inspection', 0.01)          # (probability / s) | probability to assess hive nectar level
        self.p_nectar_communication = kwargs.get('p_nectar_communication', 0.02)    # (probability / s) | probability to communicate hive nectar level to other bees
        self.exploring_incentive =kwargs.get('exploring_incentive', 0.1)            # Lambda parameter in exponential distribution going into exploration state

        self.bee_swarm_size =kwargs.get('bee_swarm_size', 20)                                           # (count) | Number of bees represented by a single BeeSwarm agent
        self.carrying_capacity = kwargs.get('carrying_capacity', 30*MILLIGRAMM * self.bee_swarm_size)   # (in kg) = 30mg per bee | Amount of resources a bee swarm can carry
        self.scent_scale_mean = kwargs.get('scent_scale_mean', 0.5)                                     # (scale) = on average 50% more focused on following scent
        self.scent_scale_std = kwargs.get('scent_scale_std', 2)                                         # (scale)
        self.field_of_view = kwargs.get('field_of_view', 1)                                             # (in m) TODO: calibrate further using real data
        self.starvation_speed = kwargs.get('starvation_speed', 1/(12*HOUR))                             # (in rate/s)
        self.max_age = kwargs.get('max_age', np.inf)                                                    # (in s) = not used
        self.p_death_by_storm = kwargs.get('p_death_by_storm', 1/(10*MINUTE))                           # (probability / s) = on average within 10 minute TODO: calibrate further
        self.p_death_by_outside_risk = kwargs.get('p_death_by_outside_risk', 1/(7*WEEK))                # (probability / s) = on average within 7 weeks TODO: calibrate further
        self.speed = kwargs.get('speed', 3.5)                                                           # (in m/s) = 12.6km/h
        self.dancing_time = kwargs.get('dancing_time', 2*MINUTE)                                        # (in s) TODO: calibrate further
        self.p_follow_wiggle_dance = kwargs.get('p_follow_wiggle_dance', 0.7)                           # (probability) TODO: calibrate further
        self.p_abort = kwargs.get('p_abort', 1/(20*MINUTE))                                             # (probability) TODO: calibrate further
        self.storm_abort_factor = kwargs.get('storm_abort_factor', 100)                                 # (scale) = 100 times more likely to abort during storm TODO: calibrate further
        self.feed_storage = kwargs.get('feed_storage', 0.01*GRAMM * self.bee_swarm_size)                # (in kg) = 0.01g per bee

class HiveConfig:
    def __init__(self, **kwargs):
        self.max_nectar_capacity = kwargs.get('max_nectar_capacity', 20)       # (in kg) | NOTE: Quantity approximately needed to survive winter, given in "Wisdom of the Hive" book.
        self.default_radius = kwargs.get('default_radius', 20)                 # (in m) | unrealistic, to enable heterogenous behavior "within" i.e. around hive at current time stepping
        self.default_nectar = kwargs.get('default_nectar', 0)                  # (in kg)
        self.init_young_bees = kwargs.get('init_young_bees', 0)                # (count) = not used
        self.p_new_forager: float = kwargs.get('p_new_forager', 0)             # (probability / s) = not used

class ResourceConfig:
    def __init__(self, **kwargs):
        self.default_quantity = kwargs.get('default_quantity', 1)              # (in kg)
        self.default_radius = kwargs.get('default_radius', 100.0)              # (in m)
        self.nectar_production_rate = kwargs.get('nectar_production_rate', 0)  # 2e-7 * np.pi * DEFAULT_RADIUS**2 / (60*60*24) # (in kg/s) | stems from this formula for flower nectar production: growth = 0.2 mg / (m^2 * day) from paper (https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2745.13598)
        self.default_persistent = kwargs.get('default_persistent', False)      # whether resources can run out

class VisualConfig:
    def __init__(self, **kwargs):
        self.render_size = kwargs.get('render_size', 600)                       # Grid size for JS visualization
        self.hive_radius = kwargs.get('hive_radius', 0.03*self.render_size)     # Hive radius for JS visualization
        self.bee_radius = kwargs.get('bee_radius', 0.002*self.render_size)      # Bee radius for JS visualization

class ModelConfig:
    def __init__(self, **kwargs):
        self.size = kwargs.get('size', 10_000)                                  # (in m)
        self.dt = kwargs.get('dt', 60)                                          # (in s)
        self.p_storm_default = kwargs.get('p_storm_default', 1/(10*DAY))        # (probability / s) = on average every 10 days
        self.storm_duration_default = kwargs.get('storm_duration_default', DAY) # (in s)
        self.n_beeswarms = kwargs.get('n_beeswarms', 500)                       # (count)
        self.n_hives = kwargs.get('n_hives', 1)                                 # (count)
        self.n_resource_sites = kwargs.get('n_resources', 10)                   # (count)
        self.n_clusters = kwargs.get('n_clusters', 2)                          # (count)
        self.clust_coeff = kwargs.get('clust_coeff', 0.7)                       # Cluster coefficient