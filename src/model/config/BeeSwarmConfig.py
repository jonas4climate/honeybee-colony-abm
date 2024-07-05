from numpy import inf
from ..util.Units import *

class BeeSwarmConfig:
    def __init__(self, **kwargs):

        # ---| General parameters |---

        # Number of bees represented by a single BeeSwarm agent
        self.bee_swarm_size = kwargs.get('bee_swarm_size', 20)
        # [s] Maximal age of a bee, by default death by aging is turned off
        self.max_age = kwargs.get('max_age', inf)

        # ---| Feeding and hunger |---

        # [1/s] Quantity deducted from in-hive bee's hunger level at each step
        self.starvation_speed = kwargs.get('starvation_speed', 1/(12*HOUR))
        # Amount of resource needed to facilitate feeding the BeeSwarm agent
        self.feed_storage = kwargs.get('feed_storage', 0.01 * GRAMM * self.bee_swarm_size)

        # ---| Waggle dancing |---

        # [s] Time spent on waggle dancing
        self.waggle_dance_length = kwargs.get('waggle_dance_length', 2*MINUTE)
        # Probability of nearby in-hive bee to follow a waggle dance
        self.p_follow_waggle_dance = kwargs.get('p_follow_waggle_dance', 0.7)

        # ---| Nectar insepection and communication with other bees |---

        # [m] Field of view of a bee in which it is capable of interacting with other bees
        self.field_of_view = kwargs.get('field_of_view', 1)
        # Bee's ability to percept resources, number of samples parameter used to calculate parameters for
        # Beta distribution, lower number leads to less precise perceived nectar values w.r.t to actual values
        self.perception = kwargs.get('perception', 100)
        # [1/s] Probability for each bee in the hive to asses nectar resources at the given simulation step
        # TODO: Adapt the value (?)
        self.p_nectar_inspection = kwargs.get('p_nectar_inspection', 0.2 * 1 / MINUTE)
        # [1/s] Probability for each bee in the hive to communicate their perceived nectar level to other bee
        # TODO: Adapt the value (?)
        self.p_nectar_communication = kwargs.get('p_nectar_communication', 1e-3)
        # Lambda parameter for the exponential distribution describing bee's incentive to explore based on perceived nectar level
        self.exploring_incentive = kwargs.get('exploring_incentive', 0.1)

        # ---| Movement outside the hive and bias towards the resources |---

        # [m/s] Amount of distance covered by the BeeSwarm agent
        self.speed = kwargs.get('speed', 3.5)
        # Mean of the sampled Gaussian scaling factor governing bee's increased incentive to move closer to the resource
        self.scent_scale_mean = kwargs.get('scent_scale_mean', 0.5)
        # SD of the sampled Gaussian scaling factor governing bee's increased incentive to move closer to the resource
        self.scent_scale_std = kwargs.get('scent_scale_std', 2)
        # [1/s] Probability for an outside bee to die from random (non weather and age related) factors
        self.p_death_by_outside_risk = kwargs.get('p_death_by_outside_risk', 1/(7*WEEK))
        # [1/s] Probability that a bee will abort exploration and return to hive
        self.p_abort = kwargs.get('p_abort', 1/(20*MINUTE))
        # Amount of resources a single BeeSwarm agent carries on a foraging trip
        self.carrying_capacity = kwargs.get('carrying_capacity', 30 * MILLIGRAMM * self.bee_swarm_size)
        
        # ---| Weather effects |---

        # [1/s] Probability for an outside bee to die during storm at each step
        self.p_death_by_storm = kwargs.get('p_death_by_storm', 1/(10*MINUTE))
        # Scaling factor for the probability to abort exploration during stormy weather
        self.storm_abort_factor = kwargs.get('storm_abort_factor', 100)

    def __str__(self):
        return 'BeeSwarmConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])