import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os
import pandas as pd
from multiprocessing.pool import Pool

from model.agents.BeeSwarm import BeeSwarm
from src.model.agents.Hive import Hive
from src.model.agents.Resource import Resource

from src.model.config.BeeSwarmConfig import BeeSwarmConfig
from src.model.config.HiveConfig import HiveConfig
from src.model.config.ResourceConfig import ResourceConfig
from src.model.config.ModelConfig import ModelConfig

from src.model.util.Units import *

from src.model.Model import ForagerModel, SpaceSetup

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

def run_simulation(params):
        p_storm, dist_from_hive = params
        model_config = ModelConfig(n_beeswarms=n_beeswarms, p_storm_default=p_storm, dt=dt, size=size,
                        n_resource_sites=n_resource_sites, space_setup=space_setup, default_persistent=default_persistent,
                        storm_duration_default=default_storm_duration)
        beeswarm_config = BeeSwarmConfig(p_abort=p_abort)
        hive_config = HiveConfig()
        resource_config = ResourceConfig()
        model = ForagerModel(model_config, hive_config, beeswarm_config, resource_config, dist_from_hive)
        for t in range(t_steps):
            model.step()
        survival_ratio = model.datacollector.model_vars['Bee count 🐝'][-1] / n_beeswarms
        return survival_ratio

if __name__ == '__main__':
    # Generate / Load results
    if not os.path.exists(mean_file):
        pbar = tqdm(total=resolution**2*N_sims, desc='Progress:')
        with Pool() as pool:
            for i, p_storm in enumerate(p_storm_params):
                for j, dist_from_hive in enumerate(res_dist_from_hive_params):
                    params_list = [(p_storm, dist_from_hive) for _ in range(N_sims)]
                    survival_ratios = pool.map(run_simulation, params_list)
                    pbar.update(N_sims)
                    mean_survival_ratios[i, j] = np.mean(survival_ratios)
                    std_survival_ratios[i, j] = np.std(survival_ratios)
            pbar.close()
            np.savetxt(mean_file, mean_survival_ratios)
            np.savetxt(std_file, std_survival_ratios)
    else:
        mean_survival_ratios = np.loadtxt(mean_file)
        std_survival_ratios = np.loadtxt(std_file)

    # Visualize results
    fig, axs = plt.subplots(1, 2, figsize=(10, 6.3))

    im0 = axs[0].imshow(mean_survival_ratios, cmap='viridis')
    plt.colorbar(im0, ax=axs[0], label='Survival ratio', orientation='horizontal', fraction=0.046, pad=0.1)
    axs[0].set_title('Mean survival ratio of bees')
    im1 = axs[1].imshow(std_survival_ratios, cmap='hot')
    plt.colorbar(im1, ax=axs[1], label='Survival ratio', orientation='horizontal', fraction=0.046, pad=0.1)
    axs[1].set_title('Standard deviation of survival ratio of bees')

    for ax in axs:
        ax.set_xlabel('Distance from hive (in km)')
        ax.set_xticks(np.arange(resolution))
        ax.set_xticklabels([f'{x/1000:.2f}' for x in res_dist_from_hive_params])
        ax.set_ylabel('Storm probability (per hour)')
        ax.set_yticks(np.arange(resolution))
        ax.set_yticklabels([f'{x*HOUR:.2f}' for x in p_storm_params])

    plt.tight_layout()
    plt.suptitle('Mean and STD of survival ratios as a function of resource distance and storm probability')
    plt.savefig('../assets/images/bee_survival_ratio_2d.png')
    plt.show()