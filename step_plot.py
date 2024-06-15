from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter
# Get parameters for the model
from set_parameters import SIZE

from basic_model import Bee, Resource, BeeHive, BeeModel

colors = {BeeHive: "#000000", Bee: "#E9AB17", Resource: "#00A36C"}

def agent_portrayal(agent):
    if agent is None:
        return
    else:
        portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true"}
        portrayal["Color"] = colors[type(agent)]
        return portrayal
    
canvas = CanvasGrid(agent_portrayal, SIZE, SIZE)


chart_colors = {1:"#000000", # Black
                2:"#008000", # Green
                3:"#E9AB17", # Yellow
                4:"#FFC0CB"} # Pink
chart_1 = ChartModule([
    {"Label": "prop_resources", "Color":chart_colors[2]},
    {"Label": "prop_foragers", "Color": chart_colors[3]},
    {"Label": "prop_baby_bees", "Color": chart_colors[4]}

])
    # {"Label": "foragers", "Color":chart_colors[3]},
    # {"Label": "baby_bees", "Color": chart_colors[4]}])
chart_2 = ChartModule([{"Label": "num_bees", "Color": chart_colors[1]},
                       {"Label": "num_resources", "Color": chart_colors[2]},
                        {"Label": "num_foragers", "Color": chart_colors[3]},
                        {"Label": "num_baby_bees", "Color": chart_colors[4]}

])



server = ModularServer(
    BeeModel,
    [canvas, chart_1, chart_2],
    "BeeModel",
    {
        "SIZE": SIZE,
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