class ResourceConfig:
    def __init__(self, **kwargs):
        self.default_quantity = kwargs.get('default_quantity', 1)              # (in kg)
        self.default_radius = kwargs.get('default_radius', 100.0)              # (in m)
        self.nectar_production_rate = kwargs.get('nectar_production_rate', 0)  # 2e-7 * np.pi * DEFAULT_RADIUS**2 / (60*60*24) # (in kg/s) | stems from this formula for flower nectar production: growth = 0.2 mg / (m^2 * day) from paper (https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2745.13598)
        self.default_persistent = kwargs.get('default_persistent', False)      # whether resources can run out

    def __str__(self):
        return 'ResourceConfig:\n' + '\n'.join([f'- {key}: {value}' for key, value in self.__dict__.items()])