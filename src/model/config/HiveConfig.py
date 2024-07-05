class HiveConfig:
    def __init__(self, **kwargs):
        self.max_nectar_capacity = kwargs.get('max_nectar_capacity', 20)       # (in kg) | NOTE: Quantity approximately needed to survive winter, given in "Wisdom of the Hive" book.
        self.default_radius = kwargs.get('default_radius', 20)                 # (in m) | unrealistic, to enable heterogenous behavior "within" i.e. around hive at current time stepping
        self.default_nectar = kwargs.get('default_nectar', 0)                  # (in kg)
        self.init_young_bees = kwargs.get('init_young_bees', 0)                # (count) = not used
        self.p_new_forager: float = kwargs.get('p_new_forager', 0)             # (probability / s) = not used

    def __str__(self):
        return 'HiveConfig\n:' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])