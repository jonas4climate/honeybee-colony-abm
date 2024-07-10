import mesa

from mesa.visualization.modules import ChartModule

from src.model.Model import ForagerModel, RunMode
from src.model.agents.BeeSwarm import BeeSwarm, BeeState
from src.model.agents.Hive import Hive
from src.model.agents.Resource import Resource

from src.model.config.ModelConfig import ModelConfig as MC
from src.model.config.VisualConfig import VisualConfig as VC

class SimpleCanvas(mesa.visualization.VisualizationElement):
    local_includes = ["./simple_continuous_canvas.js"]

    def __init__(self, canvas_height, canvas_width, portrayal_method=None):
        """
        Instantiate a new SimpleCanvas
        """
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = "new Simple_Continuous_Module({}, {})".format(
            self.canvas_width, self.canvas_height
        )
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            x, y = obj.pos
            x = (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal["x"] = x
            portrayal["y"] = y
            space_state.append(portrayal)
        return space_state

def agent_potrayal(agent):
    if isinstance(agent, BeeSwarm):
        return {"Shape": "circle", "r": VC.BEE_RADIUS, "Filled": "true", "Color": VC.BEE_COLORS[agent.state]}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": VC.HIVE_RADIUS, "Filled": "true", "Color": VC.HIVE_COLOR}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": VC.RESOURCE_RADIUS, "Filled": "true", "Color": VC.RESOURCE_COLOR(agent)}

forager_canvas = SimpleCanvas(portrayal_method=agent_potrayal, canvas_height=MC.SIZE*VC.RENDER_SCALE, canvas_width=MC.SIZE*VC.RENDER_SCALE)

model_params = {
    "p_storm": mesa.visualization.Slider(
        name="Storm probability",
        value=VC.P_STORM_DEFAULT,
        min_value=0.0,
        max_value=0.01,
        step=0.0025,
        description="What is the probability of a storm event starting in a single step",
    ),
    "storm_duration": mesa.visualization.Slider(
        name="Storm duration",
        value=VC.STORM_DURATION_DEFAULT,
        min_value=5,
        max_value=35,
        step=5,
        description="How many steps will the storm event last",
    ),
    "run_mode": RunMode.SERVER,
    "n_resources": mesa.visualization.Slider(
        name = "Number of flower patches",
        value = VC.N_RESOURCES_DEFAULT,
        min_value=1,
        max_value=10,
        step = 1),
    "resource_dist": mesa.visualization.Slider(
        name = "Distance of resources to the hive",
        value = VC.RESOURCE_DISTANCE_DEFAULT,
        min_value=20,
        max_value=140,
        step = 5),
}

# Evolving plot of number of bees, read from model_reporters
bee_number_plot = ChartModule([{"Label": "Bee count 🐝", "Color": "black"},
                               {"Label": "Storm ⛈️", "Color": "red"}])

prop_bee_plot = ChartModule([{"Label": "resting 💤", "Color": VC.BEE_COLORS[BeeState.RESTING]},
                             {"Label": "returning 🔙", "Color": VC.BEE_COLORS[BeeState.RETURNING]},
                             {"Label": "exploring 🗺️", "Color": VC.BEE_COLORS[BeeState.EXPLORING]},
                             {"Label": "carrying 🎒", "Color": VC.BEE_COLORS[BeeState.CARRYING]},
                             {"Label": "dancing 🪩", "Color": VC.BEE_COLORS[BeeState.DANCING]},
                             {"Label": "following 🎯", "Color": VC.BEE_COLORS[BeeState.FOLLOWING]}])

nectar_plot = ChartModule([{"Label": "Mean perceived nectar level", "Color": "black"}, {"Label": f"Hive stock 🍯", "Color": VC.HIVE_COLOR}])

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas, bee_number_plot, prop_bee_plot, nectar_plot],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8524