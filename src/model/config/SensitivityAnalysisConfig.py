class SensitivityAnalysisConfig:

    # Config file, defines parameter ranges for sampling in Sensitivity Analysis

    class HiveParamBounds:

        # Inital number of bees in the hive
        N_BEES_MIN = 50
        N_BEES_MAX = 400

        # Initial amount of nectar in the hive
        DEFAULT_INIT_NECTAR_MIN = 1
        DEFAULT_INIT_NECTAR_MAX = 8

    class BeeParamBounds:
        
        # ---| General parameters |---

        # Field of view of a bee in which it is capable of interacting with other bees
        FOV_MIN = 0.25
        FOV_MAX = 2.0

        # Quantity deducted from hive storage per bee in hive
        FOOD_CONSUMPTION_MIN = 0.000025
        FOOD_CONSUMPTION_MAX = 0.0002
        
        # ---| Movement |---

        # Amount of distance covered by the BeeSwarm agent in a single step inside the hive
        SPEED_IN_HIVE_MIN = 0.25
        SPEED_IN_HIVE_MAX = 2.0

        # Amount of distance covered by the BeeSwarm agent in a single step outside the hive
        SPEED_FORAGING_MIN = 1.0
        SPEED_FORAGING_MAX = 15.0

        # ---| In-hive behaviour |---

        # At least this number of steps bee will stay resting after trip outside the hive
        RESTING_PERIOD_MIN = 1
        RESTING_PERIOD_MAX = 15

        # Probability for each bee in the hive to asses nectar resources at the given simulation step
        P_NECTAR_INSPECTION_MIN = 0.05
        P_NECTAR_INSPECTION_MAX = 0.4

        # Probability for each bee in the hive to communicate their perceived nectar level to other bee
        P_NECTAR_COMMUNICATION_MIN = 0.1
        P_NECTAR_COMMUNICATION_MAX = 0.8

        # ---| Exploration and recruitment |---

        # Probability of nearby in-hive bee to follow a waggle dance
        P_FOLLOW_WAGGLE_DANCE_MIN = 0.3
        P_FOLLOW_WAGGLE_DANCE_MAX = 1.0

        # How eager the bee is to explore based on current resources
        EXPLORING_INCENTIVE_MIN = 10
        EXPLORING_INCENTIVE_MAX = 150

        # Amount of resource the Bee agent can carry
        CARRYING_CAPACITY_MIN = 0.001
        CARRYING_CAPACITY_MAX = 0.015

        # Probability that a bee will abort exploration and return to hive
        P_ABORT_MIN = 0.005
        P_ABORT_MAX = 0.04

        # ---| Birth & Death |---

        # Probability of a single new forager emerging from young population at each simulation step
        P_BIRTH_MIN = 0.1
        P_BIRTH_MAX = 0.8

        # Probability for an outside bee to die from natural factors
        P_DEATH_MIN = 0.00025
        P_DEATH_MAX = 0.002

        # Probability for an outside bee to die will be this times higher during storm
        DEATH_STORM_FACTOR_MIN = 2.5
        DEATH_STORM_FACTOR_MAX = 20