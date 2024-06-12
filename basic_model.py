"""
Starting model definition, consisting on bees, hives and resources
"""


import mesa


class Bee(mesa.Agent):
    def __init__(self, age,health,caste,location):
        super().__init__(age,health,caste,location)
        self.age = age                              # Float: number of days
        self.health = health                        # Float: [0,1]
        self.type = caste                           # String: "worker", "forager", "etc..."
        self.location = location                    # Tuple: (x,y)
        # TODO: Complete
    
    # TODO: Add method to die (based on age, health, location)
    # TODO: Add method to change type
    # TODO: Add method for every caste
    # TODO: Add method to make forager put back resource in hive

class Hive(mesa.Agent):
    def __init__(self, location, radius):
        self.location = location                    # (x,y) tuple
        self.radius = radius                        # Beehive has a circle shape, size may change with population
        # TODO: Complete    
    
class Resource(mesa.Agent):
    def __init__(self, location, type, quantity, persistent):
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
        # TODO: Complete
    