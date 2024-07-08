class ModelConfig:

    # Side length of square continuous space where the bees can forage
    SIZE = 300

    def __init__(self, **kwargs):

        # Probability of storm event occuring
        self.P_STORM = kwargs.get('P_STORM', 0.005)

        # Default duration of the storm event
        self.STORM_DURATION = kwargs.get('STORM_DURATION', 20)

        # Number of resources in the default model setup
        self.N_RESOURCES_DEFAULT = kwargs.get('N_RESOURCES_DEFAULT', 2)

        # Distance from hive to resource in the default model setup
        self.RESOURCE_DISTANCE_DEFAULT = kwargs.get('RESOURCE_DISTANCE_DEFAULT', 50)

