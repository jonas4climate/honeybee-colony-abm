

class Resource(Agent):
    def __init__(self, id, model, location, type, quantity, persistent):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
        # TODO: Complete

    def step(self):
        # Should replentish or go extinct if quantity reaches 0
        pass    

