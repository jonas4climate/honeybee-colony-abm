import mesa

from continuous_model.Model import ForagerModel
from SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import ChartModule

from continuous_model.Bee import BeeSwarm, BeeState
from continuous_model.config import *
from continuous_model.Hive import Hive
from continuous_model.Resource import Resource

visual_config = VisualConfig()
model_config = ModelConfig()
hive_config = HiveConfig()
beeswarm_config = BeeSwarmConfig()
resource_config = ResourceConfig()

def agent_potrayal(agent):
    if isinstance(agent, BeeSwarm):
        return {"Shape": "circle", "r": visual_config.bee_radius, "Filled": "true", "Color": VisualConfig.bee_colors[agent.state]}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": visual_config.hive_radius, "Filled": "true", "Color": VisualConfig.hive_color}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": agent.radius*(visual_config.render_size/model_config.size), "Filled": "true", "Color": VisualConfig.resource_color}


forager_canvas = SimpleCanvas(
    portrayal_method=agent_potrayal, canvas_height=visual_config.render_size, canvas_width=visual_config.render_size
)

model_params = {
    "model_config": model_config,
    "hive_config": hive_config,
    "beeswarm_config": beeswarm_config,
    "resource_config": resource_config,
    "p_storm": mesa.visualization.Slider(
        name="Storm probability",
        value=model_config.p_storm_default,
        min_value=0.0,
        max_value=0.1,
        step=0.001,
        description="What is the probability of a storm occuring in a single day",
    ),
    "storm_duration": mesa.visualization.Slider(
        name="Storm duration",
        value=model_config.storm_duration_default,
        min_value=1,
        max_value=1000,
        step=1,
        description="How long will the storm event last",
    ),
    "n_resources": mesa.visualization.Slider("Number of flower patches",
                                             value = model_config.n_resource_sites,
                                             min_value=0,
                                             max_value=50,
                                             step = 1),
    "n_hives": mesa.visualization.Slider("Number of hives",
                                        value = model_config.n_hives,
                                        min_value=0,
                                        max_value=10,
                                        step = 1),
    "dt": mesa.visualization.Slider("Time step",
                                      value = model_config.dt,
                                      min_value=1,
                                      max_value=60,
                                      step = 1),
}


# Evolving plot of number of bees, read from model_reporters
bee_number_plot = ChartModule([{"Label": "Bee count 🐝", "Color": "black"},
                               {"Label": "Storm ⛈️", "Color": "red"}])



prop_bee_plot = ChartModule([{"Label": "resting 💤", "Color": BeeSwarm.bee_colors[BeeState.RESTING]},
                             {"Label": "returning 🔙", "Color": BeeSwarm.bee_colors[BeeState.RETURNING]},
                             {"Label": "exploring 🗺️", "Color": BeeSwarm.bee_colors[BeeState.EXPLORING]},
                             {"Label": "carrying 🎒", "Color": BeeSwarm.bee_colors[BeeState.CARRYING]},
                             {"Label": "dancing 🪩", "Color": BeeSwarm.bee_colors[BeeState.DANCING]},
                             {"Label": "following 🎯", "Color": BeeSwarm.bee_colors[BeeState.FOLLOWING]}])

bee_fed_plot = ChartModule([{"Label": "Average feed level of bees 🐝", "Color": "black"}])

nectar_plot = ChartModule([{"Label": "Mean perceived nectar level", "Color": "black"},
                                         {"Label": f"Hive (1) stock 🍯", "Color": VisualConfig.hive_color}])

# TODO: find a way to load this dynamically so we can have more hives without recompiling
# nectar_plot = ChartModule([{"Label": f"Hive ({i+1}) stock 🍯", "Color": hive_colors[i]} for i in range(ModelConfig.N_HIVES)])
# nectar_plot = ChartModule([{"Label": f"Hive ({i+1}) stock 🍯", "Color": hive_colors[i]} for i in range(1)])

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas, bee_number_plot, prop_bee_plot, nectar_plot, bee_fed_plot],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8525