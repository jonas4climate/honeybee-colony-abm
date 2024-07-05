class VisualConfig:
    def __init__(self, **kwargs):
        self.render_size = kwargs.get('render_size', 600)                       # Grid size for JS visualization
        self.hive_radius = kwargs.get('hive_radius', 0.03*self.render_size)     # Hive radius for JS visualization
        self.bee_radius = kwargs.get('bee_radius', 0.002*self.render_size)      # Bee radius for JS visualization

    def __str__(self):
        return 'VisualConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])