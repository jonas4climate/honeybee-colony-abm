import numpy as np

from ..config.HiveConfig import HiveConfig as HC
from ..config.ResourceConfig import ResourceConfig as RC

from ..agents.Resource import Resource

@staticmethod
def add_random_resource(model, quantity: float=RC.DEFAULT_QUANTITY):
    """
    Adds resource in a random location in space, ensuring it's not overlaping with the hive.
    """
    x, y = model.hive.pos
    while model.space.get_distance((x,y), model.hive.pos) < (HC.RADIUS + RC.RADIUS):
        x, y = np.random.uniform(0, model.size, size=2)
    
    model.create_agent(Resource, (x, y), quantity=quantity)

@staticmethod
def add_resource_in_distance(model, distance: float, quantity: float=RC.DEFAULT_QUANTITY):
    """
    Adds resource in a random location in space in a given distance from the hive.
    """
    assert distance > (HC.RADIUS + RC.RADIUS), "Resources should not overlap with the hive."

    angle = np.random.uniform(0, 2 * np.pi)
    dx = distance * np.cos(angle)
    dy = distance * np.sin(angle)

    x = model.hive.pos[0] + dx
    y = model.hive.pos[1] + dy
    
    model.create_agent(Resource, (x, y), quantity=quantity)

@staticmethod
def add_n_resources_in_angle_range(model, distance: float, n_resources: float, max_angle: float, quantity: float=RC.DEFAULT_QUANTITY):
    assert distance > (HC.RADIUS + RC.RADIUS), "Resources should not overlap with the hive."

    angles = np.arange(0, max_angle, max_angle / n_resources)

    for angle in angles:
        dx = distance * np.cos(angle)
        dy = distance * np.sin(angle)

        x = model.hive.pos[0] + dx
        y = model.hive.pos[1] + dy
    
        model.create_agent(Resource, (x, y), quantity=quantity)