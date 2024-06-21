import mesa

from continuous_model.Model import ForagerModel
from SimpleContinuousModule import SimpleCanvas

from continuous_model.Bee import Bee
from continuous_model.Hive import Hive
from continuous_model.Resource import Resource


def bee_draw(agent):
    # if not agent.neighbors:  # Only for the first Frame
    #     neighbors = len(agent.model.space.get_neighbors(agent.pos, agent.vision, False))
    # else:
    #     neighbors = len(agent.neighbors)

    # if neighbors <= 1:
    #     return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}
    # elif neighbors >= 2:
    #     return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Green"}
    if isinstance(agent, Bee):
        return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "#f7df00", "gco": "source-over"}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": Hive.RADIUS, "Filled": "true", "Color": "#82817c", "gco": "source-over"}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": agent.radius, "Filled": "true", "Color": "#77dae640", "gco": "source-in"}


forager_canvas = SimpleCanvas(
    portrayal_method=bee_draw, canvas_height=500, canvas_width=500
)

model_params = {
    # "n_bees": mesa.visualization.Slider(
    #     name="Number of bees",
    #     value=100,
    #     min_value=10,
    #     max_value=200,
    #     step=5,
    #     description="Choose how many agents to include in the model",
    # ),
    "SIZE": 100,
    "n_hives": 2,
    "hive_locations": [(20,20), (50,50)],
    "n_bees_per_hive": [10, 20],
    "n_resources": 5,
    "resource_locations": [(3,3), (10, 15), (10, 20), (15, 30), (15, 20)],
    # "height": 100
    # "speed": mesa.visualization.Slider(
    #     name="Speed of Boids",
    #     value=5,
    #     min_value=1,
    #     max_value=20,
    #     step=1,
    #     description="How fast should the Boids move",
    # ),
    # "vision": mesa.visualization.Slider(
    #     name="Vision of Bird (radius)",
    #     value=10,
    #     min_value=1,
    #     max_value=50,
    #     step=1,
    #     description="How far around should each Boid look for its neighbors",
    # ),
    # "separation": mesa.visualization.Slider(
    #     name="Minimum Separation",
    #     value=2,
    #     min_value=1,
    #     max_value=20,
    #     step=1,
    #     description="What is the minimum distance each Boid will attempt to keep from any other",
    # ),
}

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8521
