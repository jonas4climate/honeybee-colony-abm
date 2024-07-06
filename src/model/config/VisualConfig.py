from .HiveConfig import HiveConfig as HC
from .ModelConfig import ModelConfig as MC
from .ResourceConfig import ResourceConfig as RC

class VisualConfig:
    def __init__(self, **kwargs):
        # Grid size for JS server visualization
        self.render_size = kwargs.get('render_size', 600)

        # Hive radius size in JS server visualization
        self.hive_radius = kwargs.get('hive_radius', HC.RADIUS / MC.SIZE * self.render_size)

        # Bee agent radius size in JS server visualization
        self.bee_radius = kwargs.get('bee_radius', 0.002 * self.render_size)

        # Resource agent radius size in JS server visualization
        self.resource_radius = kwargs.get('resource_radius', RC.RADIUS / MC.SIZE * self.render_size)

    def __str__(self):
        return 'VisualConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])