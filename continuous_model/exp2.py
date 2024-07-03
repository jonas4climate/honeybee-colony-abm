from continuous_model.Bee import BeeSwarm
from continuous_model.Hive import Hive
from continuous_model.Model import ForagerModel
from continuous_model.Resource import Resource
from continuous_model.config import *

model_config = ModelConfig(size=2000)
beeswarm_config = BeeSwarmConfig()
hive_config = HiveConfig()
resource_config = ResourceConfig()

model = ForagerModel(model_config, hive_config, beeswarm_config, resource_config, n_resources=10, n_clusters=5, clust_coeff=0.8)


if __name__ == "__main__":
    # hive_location, resource_location = model.cluster_resources(model.size, n_resources=model_config.n_resource_sites, n_clusters=model_config.n_clusters, clust_coeff=0.8)
    hive_location, resource_location = model.init_space(model.size, model.size, model_config.n_resource_sites, model_config.n_hives)
    # print(resource_location[1])
    # print(hive_location, resource_location)