class ResourceConfig:

    # Radius of the Resource agent - in that vicinity bees can forage the nectar
    RADIUS = 5

    def __init__(self, **kwargs):

        # Default quantity of resource bees can forage from a single Resource agent before it depletes
        self.QUANTITY = kwargs.get('QUANTITY', 10)
