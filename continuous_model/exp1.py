from continuous_model.Bee import BeeSwarm
from continuous_model.Hive import Hive
from continuous_model.Model import ForagerModel
from continuous_model.Resource import Resource
from continuous_model.config import *

model_config = ModelConfig(size=2000)
beeswarm_config = BeeSwarmConfig()
hive_config = HiveConfig()
resource_config = ResourceConfig()

model = ForagerModel(model_config, hive_config, beeswarm_config, resource_config)

for t in range(1000):
    model.step()