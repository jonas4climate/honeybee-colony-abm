"""
Starting model definition, consisting on bees, hives and resources
"""


import mesa


class Bee(mesa.Agent):
    def __init__(self, age,location):
        super().__init__(age,location)
        self.age = 0                                # Float: number of days
        self.health = 0                             # Float: [0,1]
        self.location = location                    # (x,y) tuple
        # TODO: Complete

class Hive(mesa.Agent):
    def __init__(self, location, radius):
        self.location = location                    # (x,y) tuple
        self.radius = radius                        # Beehive has a circle shape, size may change with population

class Resource(mesa.Agent):
    def __init__(self, location, type, quantity, persistent):
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
    