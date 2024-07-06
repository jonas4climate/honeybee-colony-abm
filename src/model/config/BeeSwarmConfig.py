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
        self.food_consumption = kwargs.get('food_consumption', 0.001)

        # ---| Waggle dancing |---

        # Probability of nearby in-hive bee to follow a waggle dance
        self.p_follow_waggle_dance = kwargs.get('p_follow_waggle_dance', 0.7)

        # ---| Nectar insepection, communication with other bees and exploration |---

        # [m] Field of view of a bee in which it is capable of interacting with other bees
        self.field_of_view = kwargs.get('field_of_view', 1)
        # Bee's ability to percept resources, number of samples parameter used to calculate parameters for
        # Beta distribution, lower number leads to less precise perceived nectar values w.r.t to actual values
        self.perception = kwargs.get('perception', 100)
        # [1/s] Probability for each bee in the hive to asses nectar resources at the given simulation step
        self.p_nectar_inspection = kwargs.get('p_nectar_inspection', 0.1)
        # [1/s] Probability for each bee in the hive to communicate their perceived nectar level to other bee
        self.p_nectar_communication = kwargs.get('p_nectar_communication', 0.1)
        # Lambda parameter for the exponential distribution describing bee's incentive to explore based on perceived nectar level
        self.exploring_incentive = kwargs.get('exploring_incentive', 0.1)
        # Maximal time spent in the ready state, awaiting for recruitment or starting exploration
        self.max_ready_time = kwargs.get('max_ready_time', 20)

        # ---| Movement and bias towards the resources |---

        # [m/s] Amount of distance covered by the BeeSwarm agent outside the hive
        self.speed = kwargs.get('speed', 3.5)
        # [m] Amount of distance covered by the BeeSwarm agent inside the hive, does not scale with time
        self.speed_in_hive = kwargs.get('speed_in_hive', 1)
        # [1/s] Probability for an outside bee to die from random (non weather and age related) factors
        self.p_death = kwargs.get('p_death_by_outside_risk', 0.01)
        # [1/s] Probability that a bee will abort exploration and return to hive
        self.p_abort = kwargs.get('p_abort', 0.01)

    def __str__(self):
        return 'BeeSwarmConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])