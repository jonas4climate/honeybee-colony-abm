from numpy import inf

class BeeSwarmConfig:
    def __init__(self, **kwargs):
        # ---| General parameters |---

        # Field of view of a bee in which it is capable of interacting with other bees
        self.FOV = kwargs.get('FOV', 1)

        # Quantity deducted from hive storage per bee in hive
        self.FOOD_CONSUMPTION = kwargs.get('FOOD_CONSUMPTION', 0.0001)
        
        # ---| Movement |---

        # Amount of distance covered by the BeeSwarm agent in a single step inside the hive
        self.SPEED_IN_HIVE = kwargs.get('SPEED_IN_HIVE', 1)

        # Amount of distance covered by the BeeSwarm agent in a single step outside the hive
        self.SPEED_FORAGING = kwargs.get('SPEED_FORAGING', 5)

        # ---| In-hive behaviour |---

        # At least this number of steps bee will stay resting after trip outside the hive
        self.RESTING_PERIOD = kwargs.get('RESTING_PERIOD', 5)

        # Probability for each bee in the hive to asses nectar resources at the given simulation step
        self.P_NECTAR_INSPECTION = kwargs.get('P_NECTAR_INSPECTION', 0.2)

        # Probability for each bee in the hive to communicate their perceived nectar level to other bee
        self.P_NECTAR_COMMUNICATION = kwargs.get('P_NECTAR_COMMUNICATION', 0.3)

        # ---| Exploration and recruitment |---

        # Probability of nearby in-hive bee to follow a waggle dance
        self.P_FOLLOW_WAGGLE_DANCE = kwargs.get('P_FOLLOW_WAGGLE_DANCE', 0.7)

        # How eager the bee is to explore based on current resources
        self.EXPLORING_INCENTIVE = kwargs.get('EXPLORING_INCENTIVE', 50)

        # Amount of resource the Bee agent can carry
        self.CARRYING_CAPACITY = kwargs.get('CARRYING_CAPACITY', 0.005)

        # Probability that a bee will abort exploration and return to hive
        self.P_ABORT = kwargs.get('P_ABORT', 0.025)

        # ---| Birth & Death |---

        # Probability of a single new forager emerging from young population at each simulation step
        self.P_BIRTH = kwargs.get('P_BIRTH', 0.2)

        # Probability for an outside bee to die from natural factors
        self.P_DEATH = kwargs.get('P_DEATH', 0.001)

        # Probability for an outside bee to die will be this times higher during storm
        self.DEATH_STORM_FACTOR = kwargs.get('DEATH_STORM_FACTOR', 10)

