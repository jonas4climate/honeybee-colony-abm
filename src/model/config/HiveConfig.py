class HiveConfig:
    def __init__(self, **kwargs):

        # [kg] Maximum amount of resources that can be stored in the hive, 20 kg is approximately
        # the quantity of nectar needed for bees to survive the winter as given in "Wisdom of the Hive" book
        self.max_nectar_capacity = kwargs.get('max_nectar_capacity', 20)

        # [m] Radius of "hive area", reflecting hive's closest vicinity where bees can communicate
        self.default_radius = kwargs.get('default_radius', 20)

        # [kg] Default amount of nectar stored in the hive
        self.default_nectar = kwargs.get('default_nectar', 0)
        
        # Probability of a new forager emerging from young population at each simulation step
        self.p_new_forager: float = kwargs.get('p_new_forager', 0)

    def __str__(self):
        return 'HiveConfig\n:' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])