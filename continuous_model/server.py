import mesa

from continuous_model.Model import ForagerModel
from SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import ChartModule

from continuous_model.Bee import Bee, BeeState
from continuous_model.config import HiveConfig, ModelConfig
from continuous_model.Hive import Hive
from continuous_model.Resource import Resource

bee_colors = {
    BeeState.RESTING : "#fc0303", # red
    BeeState.RETURNING: "#3bf55a", # green
    BeeState.EXPLORING : "#0af5f1", # blue
    BeeState.CARRYING : "#59a2c2", # light blue
    BeeState.DANCING : "#ff52df", # pink
    BeeState.FOLLOWING : "#0a54f5" # dark blue
}


def agent_potrayal(agent):
    if isinstance(agent, Bee):
        return {"Shape": "circle", "r": 2, "Filled": "true", "Color": bee_colors[agent.state]}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": HiveConfig.RADIUS, "Filled": "true", "Color": "#82817c"}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": agent.radius, "Filled": "true", "Color": "#77dae640"}


forager_canvas = SimpleCanvas(
    portrayal_method=agent_potrayal, canvas_height=500, canvas_width=500
)

model_params = {
    "size": ModelConfig.SIZE,
    "n_hives": 2,
    # "hive_locations": [(100,100), (200,250)],
    "n_bees_per_hive": ModelConfig.N_BEES,
    # "n_resources": 5,
    # "resource_locations": [(300,300), (350, 320), (325, 325), (400, 90), (380, 80)],
    "p_storm": mesa.visualization.Slider(
        name="Storm probability",
        value=ModelConfig.P_STORM_DEFAULT,
        min_value=0.0,
        max_value=0.1,
        step=0.001,
        description="What is the probability of a storm occuring in a single day",
    ),
    "storm_duration": mesa.visualization.Slider(
        name="Storm duration",
        value=ModelConfig.STORM_DURATION_DEFAULT,
        min_value=1,
        max_value=1000,
        step=1,
        description="How long will the storm event last",
    ),
    "n_resources": mesa.visualization.Slider("Number of flower patches",
                                             value = ModelConfig.N_RESOURCE_CITES,
                                             min_value=0,
                                             max_value=10,
                                             step = 1),
    "n_hives": mesa.visualization.Slider("Number of hives",
                                        value = ModelConfig.N_HIVES,
                                        min_value=0,
                                        max_value=10,
                                        step = 1),
    "dt": mesa.visualization.Slider("Time step",
                                      value = ModelConfig.DT,
                                      min_value=1,
                                      max_value=60,
                                      step = 1),
}


# Evolving plot of number of bees, read from model_reporters
bee_number_plot = ChartModule([{"Label": "Bee count 🐝", "Color": "black"},
                               {"Label": "Storm ⛈️", "Color": "red"}])



prop_bee_plot = ChartModule([{"Label": "resting 💤", "Color": bee_colors[BeeState.RESTING]},
                             {"Label": "returning 🔙", "Color": bee_colors[BeeState.RETURNING]},
                             {"Label": "exploring 🗺️", "Color": bee_colors[BeeState.EXPLORING]},
                             {"Label": "carrying 🎒", "Color": bee_colors[BeeState.CARRYING]},
                             {"Label": "dancing 🪩", "Color": bee_colors[BeeState.DANCING]},
                             {"Label": "following 🎯", "Color": bee_colors[BeeState.FOLLOWING]}])

bee_fed_plot = ChartModule([{"Label": "Average feed level of bees 🐝", "Color": "black"}])

# 10 distinct colors excluding white
hive_colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ff8000", "#ff0080", "#80ff00", "#0080ff"]
# TODO: find a way to load this dynamically so we can have more hives without recompiling
# nectar_plot = ChartModule([{"Label": f"Hive ({i+1}) stock 🍯", "Color": hive_colors[i]} for i in range(ModelConfig.N_HIVES)])
nectar_plot = ChartModule([{"Label": f"Hive ({i+1}) stock 🍯", "Color": hive_colors[i]} for i in range(1)])

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas, bee_number_plot, prop_bee_plot, bee_fed_plot, nectar_plot],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8525