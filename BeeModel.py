from random import shuffle

from mesa import Model
from mesa.datacollection import DataCollector

from Bee import Bee
from BeeHive import BeeHive
from BeeModelGrid import BeeModelGrid
from CustomScheduler import CustomScheduler
from pathfinder import astar
from Resource import Resource
from set_parameters import WIDTH, HEIGHT, RESOURCE_DENSITY, NUM_BEES


class BeeModel(Model):

    def __init__(
        self,
        width=WIDTH,
        height=HEIGHT,
        num_bees=NUM_BEES,
        resource_density=RESOURCE_DENSITY,
        nr_hives=1,
        PLOT=False,
    ):
        super().__init__()

        # grid setup
        self.height = height
        self.width = width
        self.grid = BeeModelGrid(width, height, torus=True, PLOT=PLOT)

        # environment setup
        self.hives = {}
        self.nr_hives = nr_hives
        self.resource_density = resource_density

        # agent setup
        self.agents = []
        self.dead_bees = 0
        self.born_bees = 0
        self.n_agents_existed = 0

        self.schedule = CustomScheduler(self)

        hive_location, food_location = self.init_grid(
            width, height, resource_density, nr_hives
        )

        if nr_hives == 1:
            hive = BeeHive(self, hive_location)
            self.hives[hive.unique_id] = hive
            self.add_agent(hive, hive_location)

            for _ in range(num_bees):
                self.add_bee(hive)
                hive.num_bees += 1
        else:
            for each_hive_loc in hive_location:
                hive = BeeHive(self, each_hive_loc)
                self.hives[hive.unique_id] = hive
                self.add_agent(hive, each_hive_loc)

                for _ in range(num_bees):
                    self.add_bee(hive)
                    hive.num_bees += 1

        for each_food_loc in food_location:
            food = Resource(self, each_food_loc)
            self.add_agent(food, each_food_loc)

        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        # TODO: setup scheduler to collect data (num_bees, num_resources, num_foragers, num_baby_bees etc.)
        # self.datacollector = DataCollector({
        # })

    @staticmethod
    def init_grid(width, height, resource_density, n_hives=1):
        """Initialize the grid with resources and hives."""
        positions = [(x, y) for x in range(width) for y in range(height)]
        n_positions = len(positions)
        n_resources = int((n_positions * resource_density))  # FIXME - floor or ceil?

        shuffle(positions)

        food_location = positions[0:n_resources]
        if n_hives != 1:
            i_hives = n_resources + n_hives
            hive_location = positions[n_resources:i_hives]
        else:
            hive_location = positions[n_resources + 1]
        return hive_location, food_location

    def add_agent(self, agent, location):
        """Register a new agent in the model."""
        self.agents.append(agent)
        self.grid.place_agent(agent, location)
        self.schedule.add(agent)
        self.n_agents_existed += 1

    def remove_agent(self, agent):
        """Remove an existing agent from the model."""
        if type(agent) == Bee:
            self.dead_bees += 1
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def add_bee(self, hive):
        """Add a bee to the model."""
        bee = Bee(self, location=hive.location, hive=hive)
        self.add_agent(bee, hive.location)

    def add_baby(self, hive):
        """Add a baby bee to the model."""
        bee = Bee(self, location=hive.location, hive=hive, max_age=10)
        bee.state = "baby"
        self.born_bees += 1
        hive.num_bees += 1
        self.add_agent(bee, hive.location)

    def step(self):
        """Advance the model by one time step."""
        self.schedule.step()
        # TODO: datacollector
        # self.datacollector.collect(self)
        # self.datacollector.collect(self)  # Record step variables in the DataCollector

    def run(self, steps):
        for i in range(steps):
            self.step()
