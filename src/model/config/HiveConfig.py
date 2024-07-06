class HiveConfig:

    RADIUS = 5
    P_NEW_FORAGER = 0.05

    def __init__(self, **kwargs):

        # [kg] Default amount of nectar stored in the hive
        self.default_nectar = kwargs.get('default_nectar', 5.0)
        
        # Probability of a new forager emerging from young population at each simulation step
        self.p_new_forager: float = kwargs.get('p_new_forager', 0)

    def __str__(self):
        return 'HiveConfig\n:' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])