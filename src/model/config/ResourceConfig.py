class ResourceConfig:
    def __init__(self, **kwargs):

        # [kg] Default quantity of resource bees can forage from a single Resource agent
        self.default_quantity = kwargs.get('default_quantity', 1)

        # [m] Default radius of the Resource agent - in that vicinity bees can forage the nectar
        self.default_radius = kwargs.get('default_radius', 50.0)

        # Default type of the resource - whether it is persistent or can be depleted
        self.default_persistent = kwargs.get('default_persistent', False)

    def __str__(self):
        return 'ResourceConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])