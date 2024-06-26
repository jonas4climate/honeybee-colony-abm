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
    )
}


# Evolving plot of number of bees, read from model_reporters
bee_number_plot = ChartModule([{"Label": "n_agents_existed", "Color": "black"},
                               {"Label":"weather_event","Color":"red"}])



prop_bee_plot = ChartModule([{"Label": "prop_resting", "Color": bee_colors[Bee.State.RESTING]},
                             {"Label": "prop_returning", "Color": bee_colors[Bee.State.RETURNING]},
                             {"Label": "prop_exploring", "Color": bee_colors[Bee.State.EXPLORING]},
                             {"Label": "prop_carrying", "Color": bee_colors[Bee.State.CARRYING]},
                             {"Label": "prop_dancing", "Color": bee_colors[Bee.State.DANCING]},
                             {"Label": "prop_following", "Color": bee_colors[Bee.State.FOLLOWING]}])

nectar_plot = ChartModule([{"Label": "nectar_in_hives", "Color": "blue"}])

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas,bee_number_plot, prop_bee_plot, nectar_plot], #resource_plot]
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8525