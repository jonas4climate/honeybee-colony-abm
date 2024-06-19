from BeeModelGrid import BeeModelGrid
from mesa import Model
from set_parameters import WIDTH, HEIGHT, RESOURCE_DENSITY, NUM_BEES
from mesa.datacollection import DataCollector
from CustomScheduler import CustomScheduler
from random import shuffle
from BeeHive import BeeHive
from Bee import Bee
from Resource import Resource
from pathfinder import astar

# parameters for debugging
width = WIDTH
height = HEIGHT
resource_density = RESOURCE_DENSITY
num_bees = NUM_BEES

class BeeModel(Model):
    from set_parameters import WIDTH, HEIGHT, RESOURCE_DENSITY, NUM_BEES
    def __init__(self, width=WIDTH, height=HEIGHT, num_bees=NUM_BEES, resource_density=RESOURCE_DENSITY, nr_hives=1, PLOT=False):
        super().__init__()
        self.n_agents_existed = 0  # Counter for all agents to have created, used as unique id
        self.agents = []  # List of all agents in the model
        self.hives = {}
        self.width = width
        self.height = height
        self.resource_density = resource_density
        self.grid = BeeModelGrid(width, height, torus=True, PLOT=PLOT)
        self.schedule = CustomScheduler(self)
        self.nr_hives = nr_hives

        # Information of bees introduced and removed
        self.dead_bees = 0
        self.born_bees = 0

        hive_location, food_location = self.init_grid(width, height, resource_density, nr_hives)

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

    def add_agent(self, agent, location):
        self.agents.append(agent)
        self.grid.place_agent(agent, location)
        self.schedule.add(agent)
        self.n_agents_existed += 1

    def remove_agent(self, agent):
        if type(agent) == Bee:
            self.dead_bees += 1

        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def add_bee(self, hive):
        bee = Bee(self, location=hive.location, hive=hive)
        self.add_agent(bee, hive.location)

    def add_baby(self, hive):
        bee = Bee(self, location=hive.location, hive=hive, max_age=10)
        bee.state = 'baby'
        self.born_bees += 1
        hive.num_bees += 1
        self.add_agent(bee, hive.location)

    def step(self):
        self.schedule.step()
        # self.datacollector.collect(self)

        # TODO: datacollector
        # self.datacollector.collect(self)  # Record step variables in the DataCollector

    @staticmethod
    def init_grid(width, height, resource_density, nr_hives=1):
        all_positions = [(x, y) for x in range(width) for y in range(height)]
        total_locations = len(all_positions)
        total_food = int((total_locations * resource_density))
        shuffle(all_positions)

        food_location = all_positions[0:total_food]
        if nr_hives != 1:
            index_hives = total_food + nr_hives
            hive_location = all_positions[total_food:index_hives]
        else:
            hive_location = all_positions[total_food + 1]
        return hive_location, food_location

    def run(self, steps):
        for i in range(steps):
            self.step()
