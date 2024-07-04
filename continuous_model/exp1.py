import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os
import pandas as pd

from continuous_model.Bee import BeeSwarm
from continuous_model.Hive import Hive
from continuous_model.Resource import Resource
from continuous_model.Model import ForagerModel, SpaceSetup
from continuous_model.config import *

SEED = 42

# constant params adjusted
n_beeswarms = 500
size = 10_001
n_resource_sites = 1
default_persistent = True
space_setup = SpaceSetup.FIXED_DISTANCE_FROM_HIVE
p_abort = 1/(12.5*MINUTE)
default_storm_duration = 2*HOUR

dt = MINUTE
t_steps = DAY//dt
resolution = 5
N_sims = 10

p_storm_params = np.linspace(0, 1/(2*HOUR), resolution)
res_dist_from_hive_params = np.linspace(0, (size-1)/2, resolution)

mean_survival_ratios = np.zeros((resolution, resolution))
std_survival_ratios = np.zeros((resolution, resolution))

np.random.seed(SEED)
mean_file = os.path.join('data', 'exp1', 'bee_survival_ratio.gz')
std_file = os.path.join('data', 'exp1', 'bee_survival_ratio_std.gz')

# Generate / Load results
if not os.path.exists(mean_file):
    pbar = tqdm(total=resolution**2*N_sims, desc='Progress:')
    for i, p_storm in enumerate(p_storm_params):
        for j, dist_from_hive in enumerate(res_dist_from_hive_params):
            params_list = [(p_storm, dist_from_hive) for _ in range(N_sims)]
            survival_ratios = pool.map(run_simulation, params_list)
                mean_survival_ratios[i, j, k] = np.mean(survival_ratios)
                std_survival_ratios[i, j, k] = np.std(survival_ratios)
                pbar.update(N_sims)
                model_config = ModelConfig(n_beeswarms=n_beeswarms, p_storm_default=p_storm, dt=dt, size=size,
                                n_resource_sites=n_resource_sites, space_setup=space_setup, default_persistent=default_persistent,
                                storm_duration_default=default_storm_duration)
                beeswarm_config = BeeSwarmConfig(p_abort=p_abort)
                hive_config = HiveConfig()
                resource_config = ResourceConfig()
                model = ForagerModel(model_config, hive_config, beeswarm_config, resource_config, dist_from_hive)
                for t in range(t_steps):
                    model.step()
                survival_ratios[k] = model.datacollector.model_vars['Bee count 🐝'][-1] / n_beeswarms
                pbar.update(1)
            mean_survival_ratios[i, j] = np.mean(survival_ratios)
            std_survival_ratios[i, j] = np.std(survival_ratios)
    pbar.close()
    np.savetxt(mean_file, mean_survival_ratios)
    np.savetxt(std_file, std_survival_ratios)
else:
    mean_survival_ratios = np.loadtxt(mean_file)
    std_survival_ratios = np.loadtxt(std_file)

# Visualize results
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

im0 = axs[0].imshow(mean_survival_ratios, cmap='viridis', aspect='auto')
plt.colorbar(im0, ax=axs[0])
axs[0].set_title('Mean survival ratio of bees')

im1 = axs[1].imshow(std_survival_ratios, cmap='hot', aspect='auto')
plt.colorbar(im1, ax=axs[1])
axs[1].set_title('Standard deviation of survival ratio of bees')

for ax in axs:
    ax.set_xlabel('Distance from hive (in km)')
    ax.set_xticks(np.arange(resolution))
    ax.set_xticklabels([f'{x/1000:.2f}' for x in res_dist_from_hive_params])
    ax.set_ylabel('Storm probability (per hour)')
    ax.set_yticks(np.arange(resolution))
    ax.set_yticklabels([f'{x*HOUR:.2f}' for x in p_storm_params])

plt.tight_layout()
plt.show()