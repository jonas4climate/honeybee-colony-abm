from __future__ import annotations
from enum import Enum
from typing import Optional, Tuple

from mesa import Agent, Model
from math import atan2, cos, sin
import numpy as np
from numpy.random import random, normal
from scipy.stats import beta, expon

from .Resource import Resource
from ..util.Weather import Weather
from ..config.BeeSwarmConfig import BeeSwarmConfig

class BeeState(Enum):
    RESTING = "resting"
    RETURNING = "returning"
    READY = "ready"
    EXPLORING = "exploring"
    CARRYING = "carrying"
    DANCING = "dancing"
    FOLLOWING = "following"

class BeeSwarm(Agent):

    def __init__(
        self,
        model: Model,  # model the agent belongs to
        hive,  # the Hive the Bee agent belongs to
        location: Optional[Tuple[float, float]] = None, # agent's current position
        age: float = 0,  # agent's current age (which has influence on their activity)
        state: BeeState = BeeState.RESTING,  # Bee's current activity
        wiggle: bool = False,  # whether the Bee agent is currently wiggle dancing,
    ):
        super().__init__(model.next_id() , model)

        # The hive the bee agent belongs to
        self.hive = hive

        # Agent's position in space
        self.pos = hive.pos
        assert self.pos is not None, f"Bee agent {self} initialized with None position"

        # Agent's current activity
        self.state: BeeState = state

        # Whether the bee is waggle dancing
        # TODO: Delete, this is what Beestate.DANCING is for
        self.wiggle: bool = wiggle

        # Destination of resource communicate through waggle dance recruitment
        self.wiggle_destiny: Optional[Tuple[float, float]] = None

        # Amount of time spent waggle dancing [s]
        self.dancing_time: int = 0

        # Amount of time spent in the ready state [s]
        self.ready_time: int = 0

        # Age of the BeeSwarm agent [s]
        self.age: int = age

        # Maximum age of the BeeSwarm agent [s]
        self.max_age: int = model.beeswarm_config.max_age

        # Speed of the BeeSwarm agent outside the hive [m/s]
        self.speed: float = model.beeswarm_config.speed

        # Speed of the BeeSwarm agent inside the hive [m/s]
        self.speed_in_hive: float = model.beeswarm_config.speed_in_hive

        # Reference to the set of parameters governing BeeSwarm's agent behaviour
        self.beeswarm_config = model.beeswarm_config

        # Amount of resource load carried by the agent
        self.load = 0.0

        # Agent's hunger level
        self.fed = self.beeswarm_config.feed_storage

        # Agent's sampled Gaussian scaling factor for random walk bias towards resources
        self.scent_scale = max(normal(loc=self.beeswarm_config.scent_scale_mean, scale=self.beeswarm_config.scent_scale_std), 0)

        # Agent's perceived amount of resources available in the hive
        self.perceived_nectar = 0.0

        # Agent's perception
        self.perception = model.beeswarm_config.perception

        # Agent's starvation speed
        self.starvation_speed = model.beeswarm_config.starvation_speed

        # Agents probability of nectar inspection
        self.p_nectar_inspection = model.beeswarm_config.p_nectar_inspection

        # Agent's carrying capacity
        self.carrying_capacity = model.beeswarm_config.carrying_capacity

        # Agent's exploring incentive
        self.exploring_incentive = model.beeswarm_config.exploring_incentive

        # Agent's probability of death outside hive
        self.p_death_by_outside_risk = model.beeswarm_config.p_death_by_outside_risk

        # Agent's probability of death during storm
        self.p_death_by_storm = model.beeswarm_config.p_death_by_storm

        # Agent's probability to follow waggle dance
        self.p_follow_waggle_dance = model.beeswarm_config.p_follow_waggle_dance

        # Agent's probability to abort exploration
        self.p_abort = model.beeswarm_config.p_abort

        # Scaling factor for the probability to abort exploration during stormy weather
        self.storm_abort_factor = model.beeswarm_config.storm_abort_factor

        # Inspect hive
        self.inspect_hive()

    def step(self):
        """Agent's step function required by Mesa package."""
        self.update_properties()        # Manage properties (age and fed)
        self.step_by_caste()            # Manage action based on caste
        self.manage_death()             # Manage death

    def scent_strength_at_pos(self, pos, resources, epsilon=1e-24):
        """Calculates scent (attraction) of all Resource agents at the specific position in space.

        Args:
            pos (Tuple[float, float]): position at which attraction is calculated
            resources (List[Resource]): list of resources to calculate the scent for
            epsilon (float, optional): small number to handle edge cases. Defaults to 1e-24.

        Returns:
            float: scent strength at the given position
        """

        # Obtain positions and quantities of Resource agents
        res_positions = [res.pos for res in resources]
        res_quantities = [res.quantity for res in resources]

        scent_intrigue = 0

        # Iterate over all resources
        for res_pos, res_quant in zip(res_positions, res_quantities):
            
            # Squared distance to the resource
            res_distance = self.model.space.get_distance(pos, res_pos)
            dist_squared = res_distance**2 + epsilon

            # Scent is dependent on resource quantity and squared distance to that resource
            scent = res_quant / dist_squared
            scent_intrigue += scent

        return scent_intrigue
    
    def inspect_hive(self):
        """
        Bee agent inspects the hive and samples perceived nectar level from Beta distribution.
        """

        # Mean of the Beta distribution, equal to normalized nectar level within hive
        mu = self.hive.nectar / self.hive.max_nectar_capacity
        if mu == 0:
            mu = 1e-24
        elif mu == 1:
            mu = 1 - 1e-24

        # Alpha and Beta parameters of Beta distribution, with bee's perception as the no. of samples
        a = self.perception * (mu)
        b = self.perception * (1 - mu)
        
        assert a > 0, f"Alpha parameter in Beta distribution is {a} but must be positive"
        assert b > 0, f"Beta parameter in Beta distribution is {b} but must be positive"

        # Handle edge cases
        if np.isclose(a, 0):
            a += np.finfo(np.float32).eps

        if np.isclose(b, 0):
            b += np.finfo(np.float32).eps

        # Sample perceived nectar from the Beta distribution
        self.perceived_nectar = beta.rvs(a, b) * self.hive.max_nectar_capacity

    def move_random_in_hive(self):
        """
        Moves randomly in x and y in the interval [-distance, distance]
        """
        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2 * np.pi)
        dx = self.speed_in_hive * np.cos(angle)
        dy = self.speed_in_hive * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newy = self.pos[1] + dy
        newpos = (newx, newy)
        
        # Repeat untill the new position is within the hive
        while self.model.space.get_distance(self.hive.pos, newpos) > self.hive.radius:
            angle = np.random.uniform(0, 2 * np.pi)
            dx = self.speed_in_hive * np.cos(angle)
            dy = self.speed_in_hive * np.sin(angle)

            # Calculate the new position, taking the boundaries into account
            newx = self.pos[0] + dx
            newy = self.pos[1] + dy
            newpos = (newx, newy)

        self.model.space.move_agent(self, newpos)

    def move_random_exploration(self, epsilon=1e-12):
        """
        Moves randomly in x and y in the interval [-max_movement,max_movement]
        """
        # Distance the bee agent will cover in the simulation step
        # TODO: Add stochasticity to the distance covered.
        distance = self.speed * self.model.dt

        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2 * np.pi)
        dx = distance * np.cos(angle)
        dy = distance * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newx = max(0, min(newx, self.model.size-epsilon))
        newy = self.pos[1] + dy
        newy = max(0, min(newy, self.model.size-epsilon))
        newpos = (newx, newy)

        # Calculate resource attraction bias
        resources = self.model.get_agents_of_type(Resource)
        if len(resources) == 0: # No resources left, just walk randomly
            self.model.space.move_agent(self, newpos)
        else:
            # Attraction level at current and new position
            attraction_current = self.scent_strength_at_pos(self.pos, resources)
            attraction_new = self.scent_strength_at_pos(newpos, resources)

            assert attraction_current > 0, f"Current attraction is {attraction_current} but must be > 0"
            assert 1 + self.scent_scale > 0, f"Scent scale is {self.scent_scale} but must be > 0"
            ratio = attraction_new / (attraction_current * (1 + self.scent_scale))
    
            # Metropolis algorithm
            if attraction_new > attraction_current or random() < ratio:
                assert newpos != None, f"New position for Bee agent {self} is equal to None"
                self.model.space.move_agent(self, newpos)
            else:
                pass

    @property
    def is_outside(self):
        """
        Check is the bee agent is outside the hive. Syntactic sugar.
        """
        return not self.is_close_to_hive()
    
    def is_bee_in_sight(self, bee):
        """
        Check if another bee agent is within FOV. Syntactic sugar.
        """
        return self.is_close_to(bee, self.beeswarm_config.field_of_view)
    
    def is_resource_in_sight(self, resource):
        """
        Checks if a specific resource is within FOV of the bee agent. Syntactic sugar.
        """
        return self.is_close_to(resource, resource.radius + self.beeswarm_config.field_of_view)

    def is_close_to_hive(self):
        """
        Check if the bee agent is within hive area. Syntactic sugar.
        """
        return self.is_close_to(self.hive, self.hive.radius)
    
    def is_close_to(self, agent, threshold):
        """Determines if bee agent is in close proximity to another agent.

        Args:
            agent (Agent): agent to determine proximity for
            threshold (float): proximity threshold

        Returns:
            bool: True if the bee agent is in close proximity to the other agent
        """
        return self.model.space.get_distance(self.pos, agent.pos) <= threshold
    
    def is_hive_in_sight(self):
        # TODO: Check where that method is used, sounds like flawed logic.
        """
        Determines if bee agent is within communication threshold to its hive. Syntactic sugar.
        """
        return self.is_close_to(self.hive, self.hive.radius + self.beeswarm_config.field_of_view)

    def is_close_to_resource(self, resource):
        """
        Determines if bee agent is in close proximity to specific resource. Syntactic sugar.
        """
        return self.is_close_to(resource, resource.radius)

    def move_towards_hive(self):
        """
        Moves the bee agent towards their hive. Syntactic sugar.
        """
        self.move_towards(self.hive)

    def move_towards(self, destiny_agent):
        """
        Moves deterministically in straight line towards a target location.
        """
        if destiny_agent.pos == None:
            # TODO: Do we only use move_towards() for waggle dance recruitment ? If not the line below should be deleted.
            self.wiggle_destiny = None
            self.state = BeeState.RETURNING
            return

        # Determines distance to the destination
        dx = destiny_agent.pos[0] - self.pos[0]
        dy = destiny_agent.pos[1] - self.pos[1]
        distance = (dx**2 + dy**2) ** 0.5

        # TODO: Add stochasticity to the distance covered.

        # Determines how much distance will actually be covered
        move_distance = self.speed * self.model.dt

        # Move towards the destination.
        if distance > move_distance:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + move_distance * cos(angle)
            new_y = self.pos[1] + move_distance * sin(angle)

            newpos = (new_x, new_y)
            assert newpos != None, f"New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)
        else:
            newpos = (destiny_agent.pos[0], destiny_agent.pos[1])
            assert newpos != None, f"New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)

    def step_by_caste(self):
        """Handles the bee's actions based on their current activity."""
        if self.state == BeeState.RESTING:
            return self.handle_resting()
        elif self.state == BeeState.RETURNING:
            return self.handle_returning()
        elif self.state == BeeState.READY:
            return self.handle_ready()
        elif self.state == BeeState.EXPLORING:
            return self.handle_exploring()
        elif self.state == BeeState.CARRYING:
            return self.handle_carrying()
        elif self.state == BeeState.DANCING:
            return self.handle_dancing()
        elif self.state == BeeState.FOLLOWING:
            return self.handle_following()

    def handle_resting(self):
        """
        Handles the behaviour of a bee resting in the hive.
        """
        self.move_random_in_hive()

        if random() < self.p_nectar_inspection * self.model.dt:
            # Inspect hive resources with fixed probability
            self.inspect_hive()

        elif random() < self.p_nectar_inspection * self.model.dt:
            # If not inspecting, communicate the information with random nearby bee
            nearby_bees = self.model.space.get_neighbors(self.pos, self.beeswarm_config.field_of_view, include_center=False)
            nearby_bees = [bee for bee in nearby_bees if isinstance(bee, BeeSwarm) and bee != self]

            if len(nearby_bees) > 0:
                # Pick a random neighboring bee and share the nectar perception
                random_neighbor = nearby_bees[np.random.randint(0, len(nearby_bees))]
                random_neighbor.perceived_nectar = self.perceived_nectar

        # Start exploring based on exponential distribution
        if random() < expon.sf(self.perceived_nectar / self.hive.max_nectar_capacity, scale=self.exploring_incentive):
            self.state = BeeState.READY

    def handle_returning(self):
        """
        Handles the behaviour of a bee returning to the hive without carrying resources.
        """
        if self.is_close_to_hive():
            self.state = BeeState.RESTING
        else:
            self.move_towards_hive()

    def handle_ready(self):
        """
        Handles the behaviour of a bee ready to explore or become recruited.
        """
        self.move_random_in_hive()

        # Increment time spent in a ready state
        self.ready_time += self.model.dt
        
        # If bored with being ready decide to explore or go back to resting
        if  (self.ready_time > self.beeswarm_config.max_ready_time) or (random() < self.model.READY_EXPON_SF[(self.beeswarm_config.max_ready_time - self.ready_time) // self.model.dt]):
            self.ready_time = 0
            self.state = BeeState.RESTING
            # Start exploring based on exponential distribution (other bees could have commnicated change in perceived nectar level)
            if random() < expon.sf(self.perceived_nectar / self.hive.max_nectar_capacity, scale=self.exploring_incentive):
                self.state = BeeState.EXPLORING
            else:
                self.state = BeeState.RESTING

    def handle_exploring(self):
        """
        Handles the behaviour of bee exploring the space for resources.
        """
        # Probability to abort the recruitment and return to the hive, scaled with simulation step and storm factor
        p_abort = self.beeswarm_config.p_abort * self.model.dt
        if self.model.weather == Weather.STORM:
            p_abort *= self.storm_abort_factor

        # Abort exploration with certain probability, otherwise continue moving towards the resource
        if random() < p_abort:
            self.state = BeeState.RETURNING
        else:
            self.try_gather_resources()
            self.move_random_exploration()

    def handle_carrying(self):
        """
        Handles the behaviour of bee carrying the resource back to the hive.
        """
        # TODO: If we don't vary the load, variable load can be deleted
        # TODO: This should be done before the bee start exploring. A useless if loop.

        # At the first step, gather the resources
        if self.load == 0:
            self.load = self.carrying_capacity

        # TODO: Waggle dance should be performed with probability dependent on resource profitability
        # Fly back and put the resources in the hive, then start waggle dancing
        if self.is_close_to_hive():
            self.hive.nectar = min(self.hive.nectar + self.load, self.hive.max_nectar_capacity)
            self.load = 0
            self.wiggle = True
            self.state = BeeState.DANCING
            self.model.wiggle_dancing_bees.add(self)
        else:
            self.move_towards_hive()

    def handle_dancing(self):
        """
        Handles the behaviour of a waggle dancing bee.
        """
        # TODO: This sucks. Does not work properly if waggle_dance_length is not divisible by dt

        # Increment time spent dancing
        self.dancing_time += self.model.dt
        
        # If done waggle dancing, start resting
        if self.dancing_time >= self.beeswarm_config.waggle_dance_length:
            self.dancing_time = 0
            self.wiggle_destiny = None
            self.wiggle = False
            self.state = BeeState.RESTING
            self.model.wiggle_dancing_bees.remove(self)
        else:
            # Find nearby ready bees and try to employ them with certain probability
            nearby_ready_bees = self.model.space.get_neighbors(self.pos, self.beeswarm_config.field_of_view, include_center=False)
            nearby_ready_bees = list(filter(lambda bee : isinstance(bee, BeeSwarm) and bee.state == BeeState.READY, nearby_ready_bees))

            for bee in nearby_ready_bees:
                if random() < self.p_follow_waggle_dance * self.model.dt:
                    bee.wiggle_destiny = self.wiggle_destiny
                    bee.state = BeeState.FOLLOWING

    def handle_following(self):
        """
        Handles the behaviour of a bee recruited through waggle dance.
        """
        # Check safely if close to resource (could have disappeared), carry resource if arrived
        if self.wiggle_destiny and self.is_close_to_resource(self.wiggle_destiny):
            self.state = BeeState.CARRYING

        # Probability to abort the recruitment and return to the hive, scaled with simulation step and storm factor
        p_abort_following = self.p_abort * self.model.dt
        if self.model.weather == Weather.STORM:
            p_abort_following *= self.storm_abort_factor

        # Abort recruitment with certain probability, otherwise continue moving towards the resource
        if random() < p_abort_following:
            self.state = BeeState.RETURNING
        else:
            self.move_towards(self.wiggle_destiny)

    # def try_follow_wiggle_dance(self):
    #     """
    #     Checks if waggle dancing bee is in close proximity and becomes a recruit with certain probability.
    #     """
    #     # TODO: This is not the correct way to go. This is computationally expensive. This sucks.
    #     # This should be treated from the waggle dancer perspective, not a random bee in the hive. This should be changed  in optimization commit.
    #     dancing_bees = list(self.model.wiggle_dancing_bees)
    #     np.random.shuffle(dancing_bees)

    #     for bee in list(dancing_bees):
    #         if self.is_bee_in_sight(bee) and random() < self.p_follow_waggle_dance:
    #             self.wiggle_destiny = bee.wiggle_destiny
    #             self.state = BeeState.FOLLOWING
    #             return

    def try_gather_resources(self):
        """
        Checks if the bee is nearby Resource agents and attempts to extract one of them.
        """
        # TODO: This is not the correct way to go. This is computationally expensive. This sucks.
        # Mesa's space module has get_neighborhood() function specifically for that purpose. This should be changed in optimization commit.
        # Also, this should be handled from Resource agent perspective. Optimal computationally.
        resources = self.model.get_agents_of_type(Resource)
        for res in resources:
            if self.is_close_to_resource(res):
                self.wiggle_destiny = res
                self.state = BeeState.CARRYING
                self.extract(res)
                return
            
    def extract(self, resource: Resource):
        """Extracts nectar from a Resource agent.

        Args:
            resource (Resource): agent to extract nectar from
        """
        
        if resource.persistent == True:
            # If resource is persistent, quantity is essentially infinite
            self.load = self.carrying_capacity
        else:
            # Otherwise we take at most as much as there is available
            extract_amount = min(resource.quantity, self.carrying_capacity)
            self.load = extract_amount
            resource.quantity -= extract_amount
            resource.extracted_nectar += extract_amount
            # print(f'Resource quantity: {resource.quantity} | {self} gathered {extract_amount}')

            # If resource is depleted, remove it
            if not resource.persistent and resource.quantity <= 0:
                resource._remove_agent()

    def update_properties(self):
        """Updates the properties of the bee."""
        # Update hunger level, ensuring it's non-negative
        self.fed = max(self.fed - self.fed * self.starvation_speed * self.model.dt, 0)

        self.age += self.model.dt

    def manage_death(self):
        """Handles tiny bee deaths."""
        if self.fed == 0:  # Death by starvation
            # print("Bee died by starvation")
            return self._remove_agent()

        """Handles death of BeeSwarm agent."""
        # Death by starvation
        if self.fed == 0:
            return self._remove_agent()

        # Death by age
        if self.age >= self.max_age:
            return self._remove_agent()

        # Death by storm
        if (self.model.weather == Weather.STORM and self.is_outside):
            if random() < self.p_death_by_storm * self.model.dt:
                # print("Bee died by storm")
                return self._remove_agent()
        
        # Death by random outside risk
        if (self.is_outside and random() < self.p_death_by_outside_risk * self.model.dt):
            # print("Bee died by outside risk")
            return self._remove_agent()

    def _remove_agent(self):
        """Helper for removing agents."""
        self.model.n_agents_existed -= 1
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        self.model.agents.remove(self)
        self.remove()
