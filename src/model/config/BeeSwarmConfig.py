from numpy import inf
from ..util.Units import *

class BeeSwarmConfig:
    def __init__(self, **kwargs):
        # TODO: back up with beta probability theory
        self.perception = kwargs.get('perception', 100)                             # Perception (no. of samples parameter) for generating alpha, beta (Beta distribution) in hive inspection
        self.p_nectar_inspection = kwargs.get('p_nectar_inspection', 0.01)          # (probability / s) | probability to assess hive nectar level
        self.p_nectar_communication = kwargs.get('p_nectar_communication', 0.02)    # (probability / s) | probability to communicate hive nectar level to other bees
        self.exploring_incentive =kwargs.get('exploring_incentive', 0.1)            # Lambda parameter in exponential distribution going into exploration state

        self.bee_swarm_size = kwargs.get('bee_swarm_size', 20)                                          # (count) | Number of bees represented by a single BeeSwarm agent
        self.carrying_capacity = kwargs.get('carrying_capacity', 30*MILLIGRAMM * self.bee_swarm_size)   # (in kg) = 30mg per bee | Amount of resources a bee swarm can carry
        self.scent_scale_mean = kwargs.get('scent_scale_mean', 0.5)                                     # (scale) = on average 50% more focused on following scent
        self.scent_scale_std = kwargs.get('scent_scale_std', 2)                                         # (scale)
        self.field_of_view = kwargs.get('field_of_view', 1)                                             # (in m) TODO: calibrate further using real data
        self.starvation_speed = kwargs.get('starvation_speed', 1/(12*HOUR))                             # (in rate/s)
        self.max_age = kwargs.get('max_age', inf)                                                    # (in s) = not used
        self.p_death_by_storm = kwargs.get('p_death_by_storm', 1/(10*MINUTE))                           # (probability / s) = on average within 10 minute TODO: calibrate further
        self.p_death_by_outside_risk = kwargs.get('p_death_by_outside_risk', 1/(7*WEEK))                # (probability / s) = on average within 7 weeks TODO: calibrate further
        self.speed = kwargs.get('speed', 3.5)                                                           # (in m/s) = 12.6km/h
        self.dancing_time = kwargs.get('dancing_time', 2*MINUTE)                                        # (in s) TODO: calibrate further
        self.p_follow_wiggle_dance = kwargs.get('p_follow_wiggle_dance', 0.7)                           # (probability) TODO: calibrate further
        self.p_abort = kwargs.get('p_abort', 1/(20*MINUTE))                                             # (probability) TODO: calibrate further
        self.storm_abort_factor = kwargs.get('storm_abort_factor', 100)                                 # (scale) = 100 times more likely to abort during storm TODO: calibrate further
        self.feed_storage = kwargs.get('feed_storage', 0.01*GRAMM * self.bee_swarm_size)                # (in kg) = 0.01g per bee

    def __str__(self):
        return 'BeeSwarmConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])