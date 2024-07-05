from ..util.Units import *
from ..util.SpaceSetup import SpaceSetup

class ModelConfig:
    def __init__(self, **kwargs):
        # [m] Side length of square continuous space where the bees can forage
        self.size = kwargs.get('size', 10_000)

        # [s] Time step of the simulations
        self.dt = kwargs.get('dt', MINUTE)

        # [1/s] Probability of storm occuring at each simulation step
        self.p_storm_default = kwargs.get('p_storm_default', 1/(10*DAY))

        # [1/s] Default duration of the storm event
        self.storm_duration_default = kwargs.get('storm_duration_default', DAY)

        # Default number of beeswarms spawned within the single Hive agent
        self.n_beeswarms = kwargs.get('n_beeswarms', 500)

        # Default number of hives spawned in the simulation
        self.n_hives = kwargs.get('n_hives', 1)

        # Default number of resource sites spawned in the simulation
        self.n_resource_sites = kwargs.get('n_resource_sites', 10)

        # Helper parameter, type of space setup depending on the experiment
        self.space_setup = kwargs.get('space_setup', SpaceSetup.RANDOM)

    def __str__(self):
        return 'ModelConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])