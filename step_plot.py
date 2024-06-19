from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
# from mesa.visualization.UserParam import UserSettableParameter
# Get parameters for the model
from set_parameters import WIDTH, HEIGHT, NUM_BEES, RESOURCE_DENSITY, NR_HIVES
from model import BeeModel; from Bee import Bee; from BeeHive import BeeHive; from Resource import Resource

colors = {BeeHive: "#000000", Bee: "#E9AB17", Resource: "#00A36C"}

def agent_portrayal(agent):
    if agent is None:
        return
    else:
        portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true"}
        portrayal["Color"] = colors[type(agent)]
        return portrayal
    
canvas = CanvasGrid(agent_portrayal, WIDTH, HEIGHT)

chart_colors = {1:"#000000", # Black
                2:"#008000", # Green
                3:"#E9AB17", # Yellow
                4:"#FFC0CB"} # Pink

    # {"Label": "foragers", "Color":chart_colors[3]},
    # {"Label": "baby_bees", "Color": chart_colors[4]}])

all_agents = ChartModule([{"Label": "num_bees", "Color": chart_colors[1]},
                       {"Label": "num_resources", "Color": chart_colors[2]},
                        {"Label": "num_foragers", "Color": chart_colors[3]},
                        {"Label": "num_baby_bees", "Color": chart_colors[4]}],
                      data_collector_name = "datacollecter")

model_instance = BeeModel(width=WIDTH, height=HEIGHT, num_bees=NUM_BEES,
                          resource_density=RESOURCE_DENSITY, nr_hives=NR_HIVES, PLOT=True)
# model_instance.datacollector

prop_bees = ChartModule([
    {"Label": "prop_resources", "Color":chart_colors[2]},
    {"Label": "prop_foragers", "Color": chart_colors[3]},
    {"Label": "prop_baby_bees", "Color": chart_colors[4]}

])



server = ModularServer(
    BeeModel,
    [canvas, all_agents, prop_bees],
    "BeeModel",
    {
        "width": WIDTH,
        "height": HEIGHT,
        "num_bees": NUM_BEES,
        "resource_density": RESOURCE_DENSITY,
        "nr_hives": NR_HIVES,
        "PLOT": True
        # "height":HEIGHT,
        # "temperature": UserSettableParameter("slider",
        #                                      "temperature",
        #                                      value = 25,
        #                                      min_value=25,
        #                                      max_value=50),
        # "resource_density": UserSettableParameter("slider",
        #                                           "resource_density",
        #                                           value=0,
        #                                           min_value=0,
        #                                           max_value=100),
        
    }
    
)



if __name__ == "__main__":
    # SIZE = 50
    server.port = 5000
    server.launch()