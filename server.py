import mesa

from SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import ChartModule

from src.model.Model import ForagerModel
from src.model.agents.BeeSwarm import BeeSwarm, BeeState
from src.model.agents.Hive import Hive
from src.model.agents.Resource import Resource

from src.model.config.ModelConfig import ModelConfig as MC
from src.model.config.VisualConfig import VisualConfig as VC
from src.model.config.VisualConfig import VisualMode, BEE_COLORS, HIVE_COLOR, RESOURCE_COLOR

def agent_potrayal(agent):
    if isinstance(agent, BeeSwarm):
        return {"Shape": "circle", "r": VC.BEE_RADIUS, "Filled": "true", "Color": BEE_COLORS[agent.state]}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": VC.HIVE_RADIUS, "Filled": "true", "Color": HIVE_COLOR}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": VC.RESOURCE_RADIUS, "Filled": "true", "Color": RESOURCE_COLOR(agent)}

forager_canvas = SimpleCanvas(portrayal_method=agent_potrayal, canvas_height=MC.SIZE*VC.RENDER_SCALE, canvas_width=MC.SIZE*VC.RENDER_SCALE)

model_params = {
    "p_storm": mesa.visualization.Slider(
        name="Storm probability",
        value=MC.P_STORM_DEFAULT,
        min_value=0.0,
        max_value=0.1,
        step=0.1,
        description="What is the probability of a storm event starting in a single step",
    ),
    "storm_duration": mesa.visualization.Slider(
        name="Storm duration",
        value=MC.STORM_DURATION_DEFAULT,
        min_value=5,
        max_value=25,
        step=1,
        description="How many steps will the storm event last",
    ),
    "viz_mode": VisualMode.SERVER,
    "n_resources": mesa.visualization.Slider(
        name = "Number of flower patches",
        value = MC.N_RESOURCES_DEFAULT,
        min_value=1,
        max_value=10,
        step = 1),
    "resource_dist": mesa.visualization.Slider(
        name = "Distance of resources to the hive",
        value = MC.RESOURCE_DISTANCE_DEFAULT,
        min_value=20,
        max_value=90,
        step = 5),
}

# Evolving plot of number of bees, read from model_reporters
bee_number_plot = ChartModule([{"Label": "Bee count 🐝", "Color": "black"},
                               {"Label": "Storm ⛈️", "Color": "red"}])

prop_bee_plot = ChartModule([{"Label": "resting 💤", "Color": BEE_COLORS[BeeState.RESTING]},
                             {"Label": "returning 🔙", "Color": BEE_COLORS[BeeState.RETURNING]},
                             {"Label": "exploring 🗺️", "Color": BEE_COLORS[BeeState.EXPLORING]},
                             {"Label": "carrying 🎒", "Color": BEE_COLORS[BeeState.CARRYING]},
                             {"Label": "dancing 🪩", "Color": BEE_COLORS[BeeState.DANCING]},
                             {"Label": "following 🎯", "Color": BEE_COLORS[BeeState.FOLLOWING]}])

nectar_plot = ChartModule([{"Label": "Mean perceived nectar level", "Color": "black"}, {"Label": f"Hive stock 🍯", "Color": HIVE_COLOR}])

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas, bee_number_plot, prop_bee_plot, nectar_plot],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8524