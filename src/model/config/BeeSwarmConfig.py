from numpy import inf

class BeeSwarmConfig:

    # ---| General parameters |---

    # Field of view of a bee in which it is capable of interacting with other bees
    FOV = 1

   # Quantity deducted from hive storage per bee in hive
    FOOD_CONSUMPTION = 0.0001
    
    # ---| Movement |---

    # Amount of distance covered by the BeeSwarm agent in a single step inside the hive
    SPEED_IN_HIVE = 1

    # Amount of distance covered by the BeeSwarm agent in a single step outside the hive
    SPEED_FORAGING = 5

    # ---| In-hive behaviour |---

    # At least this number of steps bee will stay resting after trip outside the hive
    RESTING_PERIOD = 5

    # Probability for each bee in the hive to asses nectar resources at the given simulation step
    P_NECTAR_INSPECTION = 0.2

    # Probability for each bee in the hive to communicate their perceived nectar level to other bee
    P_NECTAR_COMMUNICATION = 0.3

    # ---| Exploration and recruitment |---

    # Probability of nearby in-hive bee to follow a waggle dance
    P_FOLLOW_WAGGLE_DANCE = 0.7

    # How eager the bee is to explore based on current resources
    EXPLORING_INCENTIVE = 50

    # Amount of resource the Bee agent can carry
    CARRYING_CAPACITY = 0.005

    # Probability that a bee will abort exploration and return to hive
    P_ABORT = 0.025

    # ---| Death |---

    # Probability for an outside bee to die from natural factors
    P_DEATH = 0.00

    # Probability for an outside bee to die will be this times higher during storm
    DEATH_STORM_FACTOR = 10

