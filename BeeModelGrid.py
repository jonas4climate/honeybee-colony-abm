from mesa.space import MultiGrid

from Bee import Bee
from BeeHive import BeeHive
from Resource import Resource


class BeeModelGrid(MultiGrid):
    def __init__(self, width, height, torus, PLOT=False):
        super().__init__(width, height, torus)
        self.width = width
        self.height = height
        self.torus = torus
        
        self.PLOT = PLOT

        if self.PLOT:
            self.grids = {
                Bee: [[set() for _ in range(self.height)] for _ in range(self.width)],
                BeeHive: [[set() for _ in range(self.height)] for _ in range(self.width)],
                Resource: [[None for _ in range(self.height)] for _ in range(self.width)]
            }

        else:
            self.grids = {
                Resource: [[None for _ in range(self.height)] for _ in range(self.width)]
            }
