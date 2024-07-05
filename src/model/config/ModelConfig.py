from ..util.Units import *
from ..util.SpaceSetup import SpaceSetup

class ModelConfig:
    def __init__(self, **kwargs):
        self.size = kwargs.get('size', 10_000)                                  # (in m)
        self.dt = kwargs.get('dt', MINUTE)                                      # (in s)
        self.p_storm_default = kwargs.get('p_storm_default', 1/(10*DAY))        # (probability / s) = on average every 10 days
        self.storm_duration_default = kwargs.get('storm_duration_default', DAY) # (in s)
        self.n_beeswarms = kwargs.get('n_beeswarms', 500)                       # (count)
        self.n_hives = kwargs.get('n_hives', 1)                                 # (count)
        self.n_resource_sites = kwargs.get('n_resource_sites', 10)              # (count)
        self.space_setup = kwargs.get('space_setup', SpaceSetup.RANDOM)         # SpaceSetup enum

    def __str__(self):
        return 'ModelConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])