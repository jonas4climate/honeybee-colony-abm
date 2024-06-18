# import mesa
from mesa import Agent
# from mesa.space import ContinuousSpace
# from mesa.datacollection import DataCollector

class Resource(Agent):
    def __init__(self, id, model, location, type, quantity, persistent):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
        
        def step(self):
            # 1. Depletion, if quantity reaches 0
            if not self.persistent and self.quantity <= 0:
                self.model.schedule.remove(self)

        def get_type(self):
            # 1. First method called by bees to extract the resource
            return self.type

        def extraction(self,bee_carrying_capacity):
            # 2. Second method called by bees to extract the resource            
            if self.persistent == True:
                return bee_carrying_capacity
            elif quantity <= bee_carrying_capacity:
                return quantity
            else:
                quantity -= bee_carrying_capacity
                return bee_carrying_capacity