class HiveConfig:

    # Radius of "hive area", reflecting hive's closest vicinity where bees can communicate
    RADIUS = 5

    def __init__(self, **kwargs):
        # Number of Bee agents in the hive at the simulation start
        self.N_BEES = kwargs.get('N_BEES', 200)

        # Default initial amount of nectar stored in the hive at the start of the simulation
        self.DEFAULT_INIT_NECTAR = kwargs.get('DEFAULT_INIT_NECTAR', 5.0)

        # Probability of a new forager emerging from young population at each simulation step
        self.P_BIRTH = kwargs.get('P_BIRTH', 0.2)
    
        