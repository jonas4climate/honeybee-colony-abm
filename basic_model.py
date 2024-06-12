"""
Starting model definition, consisting on bees, hives and resources
"""


import mesa
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector


class Bee(mesa.Agent):
    def __init__(self, age,health,caste,location,BeeHive):
        #super().__init__(age,health,caste,location,BeeHive)
        self.age = age                              # Float: number of days
        self.health = health                        # Float: [0,1]
        self.caste = caste                          # String: "worker", "forager", "etc..."
        self.location = location                    # Tuple: (x,y)
        self.hive = BeeHive                         # Hive: the hive the bee belongs to
        # TODO: Complete

    def step(self):
        pass    
    # TODO: Add method to die (based on age, health, location)
    # TODO: Add method to change type
    # TODO: Add method for every caste
    # TODO: Add method to make forager put back resource in hive

class BeeHive(mesa.Agent):
    def __init__(self, location, radius):
        self.location = location                    # (x,y) tuple
        self.radius = radius                        # Beehive has a circle shape, size may change with population
        # TODO: Complete    

    def step(self):
        pass

class Resource(mesa.Agent):
    def __init__(self, location, type, quantity, persistent):
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
        # TODO: Complete

    def step(self):
        # Should replentish or go extinct if quantity reaches 0
        pass    




# TODO: Define model, including step
class BeeModel(mesa.Model):

    def __init__(self, SIZE,beehives, bees, resources):
        super().__init__()
        self.size = SIZE                                        # Int: Size of the square space considered for the simulation
        self.space = ContinuousSpace(SIZE, SIZE, True)

        # Add the beehives, bees and resouces to the space
        for beehive in beehives:                                
            self.space.place_agent(beehive, beehive.location)

        for bee in bees:            
            self.space.place_agent(bee, bee.location)
            #TODO: self.schedule.add(bee)                              # Bees are also added to the agent reporters
        
        for resource in resources:
            self.space.place_agent(resource, resource.location)


        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        self.datacollector = DataCollector(
            model_reporters={},             # Collect metrics from literature at every step
            agent_reporters={}              # As well as bee agent information
        )

    def step(self):
        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector
        # TODO: self.schedule.step()