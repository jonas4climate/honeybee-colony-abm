import mesa

from continuous_model.Model import ForagerModel
from SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import ChartModule


from continuous_model.Bee import Bee
from continuous_model.Hive import Hive
from continuous_model.Resource import Resource

bee_colors = {
    Bee.State.RESTING : "#fc0303", # red
    Bee.State.RETURNING: "#3bf55a", # green
    Bee.State.EXPLORING : "#0af5f1", # blue
    Bee.State.CARRYING : "#59a2c2", # light blue
    Bee.State.DANCING : "#ff52df", # pink
    Bee.State.FOLLOWING : "#0a54f5" # dark blue
}


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
        return {"Shape": "circle", "r": 2, "Filled": "true", "Color": bee_colors[agent.state]}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": Hive.RADIUS, "Filled": "true", "Color": "#82817c"}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": agent.radius, "Filled": "true", "Color": "#77dae640"}


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
    "SIZE": 500,
    "n_hives": 2,
    "hive_locations": [(100,100), (200,250)],
    "n_bees_per_hive": [20, 50],
    "n_resources": 5,
    "resource_locations": [(300,300), (350, 320), (325, 325), (400, 90), (380, 80)],
    "p_storm": mesa.visualization.Slider(
        name="Storm probability",
        value=ForagerModel.P_STORM_DEFAULT,
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        description="What is the probability of a storm occuring in a single day",
    ),
    "storm_duration": mesa.visualization.Slider(
        name="Storm duration",
        value=ForagerModel.STORM_DURATION_DEFAULT,
        min_value=1,
        max_value=50,
        step=1,
        description="How long will the storm event last",
    ),
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


# Evolving plot of number of bees, read from model_reporters
bee_number_plot = ChartModule([{"Label": "n_agents_existed", "Color": "black"},
                               {"Label":"weather_event","Color":"red"}])



server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas,bee_number_plot],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8524