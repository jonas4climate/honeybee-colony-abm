class ResourceConfig:
    def __init__(self, **kwargs):

        # [kg] Default quantity of resource bees can forage from a single Resource agent
        self.default_quantity = kwargs.get('default_quantity', 1)

    def __str__(self):
        return 'ResourceConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])