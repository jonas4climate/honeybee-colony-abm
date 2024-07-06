import mesa

from SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import ChartModule

from src.model.Model import ForagerModel
from src.model.agents.BeeSwarm import BeeSwarm, BeeState
from src.model.agents.Hive import Hive
from src.model.agents.Resource import Resource

from src.model.config.BeeSwarmConfig import BeeSwarmConfig as BSC
from src.model.config.HiveConfig import HiveConfig as HC
from src.model.config.ResourceConfig import ResourceConfig as RC
from src.model.config.ModelConfig import ModelConfig as MC
from src.model.config.VisualConfig import VisualConfig as VC

# TODO: Should be part of visual config
bee_colors = {
    BeeState.RESTING : "#fc0303", # red
    BeeState.RETURNING: "#3bf55a", # green
    BeeState.EXPLORING : "#0af5f1", # blue
    BeeState.CARRYING : "#59a2c2", # light blue
    BeeState.DANCING : "#ff52df", # pink
    BeeState.FOLLOWING : "#0a54f5" # dark blue
}

# TODO: Should be part of visual config
hive_colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ff8000", "#ff0080", "#80ff00", "#0080ff"]

visual_config = VC()
model_config = MC()
hive_config = HC()
beeswarm_config = BSC()
resource_config = RC()

def agent_potrayal(agent):
    if isinstance(agent, BeeSwarm):
        return {"Shape": "circle", "r": visual_config.bee_radius, "Filled": "true", "Color": bee_colors[agent.state]}
    elif isinstance(agent, Hive):
        return {"Shape": "circle", "r": visual_config.hive_radius, "Filled": "true", "Color": "#82817c"}
    elif isinstance(agent, Resource):
        return {"Shape": "circle", "r": visual_config.resource_radius, "Filled": "true", "Color": "#d1bcf9"}


forager_canvas = SimpleCanvas(portrayal_method=agent_potrayal, canvas_height=MC.SIZE*visual_config.render_scale, canvas_width=MC.SIZE*visual_config.render_scale)

model_params = {
    "model_config": model_config,
    "hive_config": hive_config,
    "beeswarm_config": beeswarm_config,
    "resource_config": resource_config,
    "distance_from_hive": 100,
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
    # "n_hives": mesa.visualization.Slider("Number of hives",
    #                                     value = model_config.n_hives,
    #                                     min_value=0,
    #                                     max_value=10,
    #                                     step = 1),
    "dt": mesa.visualization.Slider("Time step",
                                      value = model_config.dt,
                                      min_value=1,
                                      max_value=60,
                                      step = 1),
    ##  Uncomment when clustering resources
    # "n_clusters": mesa.visualization.Slider("Number of clusters",
    #                                     value = model_config.n_clusters,
    #                                     min_value=0,
    #                                     max_value=5,
    #                                     step = 1),
    # "clust_coeff": mesa.visualization.Slider("Cluster coefficient",
    #                                     value = model_config.clust_coeff,
    #                                     min_value=0,
    #                                     max_value=1,
    #                                     step = 0.1),
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

nectar_plot = ChartModule([{"Label": "Mean perceived nectar level", "Color": "black"},
                                         {"Label": f"Hive (1) stock 🍯", "Color": hive_colors[0]}])

# TODO: find a way to load this dynamically so we can have more hives without recompiling
# nectar_plot = ChartModule([{"Label": f"Hive ({i+1}) stock 🍯", "Color": hive_colors[i]} for i in range(ModelConfig.N_HIVES)])
# nectar_plot = ChartModule([{"Label": f"Hive ({i+1}) stock 🍯", "Color": hive_colors[i]} for i in range(1)])

server = mesa.visualization.ModularServer(
    model_cls=ForagerModel,
    visualization_elements=[forager_canvas, bee_number_plot, prop_bee_plot, nectar_plot, bee_fed_plot],
    name="Forager Bee Model",
    model_params=model_params,
)

server.port=8524