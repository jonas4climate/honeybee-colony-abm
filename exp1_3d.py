import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from tqdm import tqdm
import os
from multiprocess.pool import Pool

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
default_storm_duration = 2*HOUR

dt = MINUTE
t_steps = DAY//dt
resolution = 4
N_sims = 10

p_storm_params = np.linspace(0, 1/(2*HOUR), resolution)
res_dist_from_hive_params = np.linspace(0, (size-1)/2, resolution)
p_abort_params = np.linspace(1/(20*MINUTE), 1/(5*MINUTE), resolution)

mean_survival_ratios = np.zeros((resolution, resolution, resolution))
std_survival_ratios = np.zeros((resolution, resolution, resolution))

np.random.seed(SEED)
mean_file = os.path.join('data', 'exp1', 'bee_survival_ratio_3d.npy')
std_file = os.path.join('data', 'exp1', 'bee_survival_ratio_std_3d.npy')

def run_simulation(params):
    p_storm, dist_from_hive, p_abort = params
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

def visualize_results(data, name: str, cmap):
    step = data.shape[2] // resolution

    fig, axs = plt.subplots(1, resolution, figsize=(16, 5), sharey='row')
    images = []
    for i, ax in enumerate(axs):
        slice_idx = i * step
        slice_data = data[:, :, slice_idx]
        img = ax.imshow(slice_data, cmap=cmap)
        images.append(img)
        ax.set_title(f'abort probability (per min) = {p_abort_params[slice_idx]*MINUTE:.2f}', fontsize=11)
        ax.set_xlabel('distance from hive (in km)')
        ax.set_xticks(np.arange(resolution))
        ax.set_xticklabels([f'{dist_from_hive/1000:.2f}' for dist_from_hive in res_dist_from_hive_params])
        if i == 0:
            ax.set_ylabel('storm probability (per hour)')
        ax.set_yticks(np.arange(resolution))
        ax.set_yticklabels([f'{p_storm*HOUR:.2f}' for p_storm in p_storm_params])

    fig.colorbar(images[-1], ax=axs, orientation='horizontal', fraction=.1, label=f'{name} of survival ratio', pad=0.2, shrink=0.5)
    plt.suptitle(f'{name} of survival ratios as a function of resource distance, storm and abort probabilities after {t_steps*dt/DAY} day(s)')
    plt.savefig(f'../assets/images/bee_survival_ratio_3d_{name}.png')
    plt.show()

if __name__ == '__main__':
    # Generate / Load results
    if not os.path.exists(mean_file):
        pbar = tqdm(total=resolution**3*N_sims, desc='Progress:')
        with Pool() as pool:
            for i, p_storm in enumerate(p_storm_params):
                for j, dist_from_hive in enumerate(res_dist_from_hive_params):
                    for k, p_abort in enumerate(p_abort_params):
                        params_list = [(p_storm, dist_from_hive, p_abort) for _ in range(N_sims)]
                        survival_ratios = pool.map(run_simulation, params_list)
                        mean_survival_ratios[i, j, k] = np.mean(survival_ratios)
                        std_survival_ratios[i, j, k] = np.std(survival_ratios)
                        pbar.update(N_sims)
        pbar.close()
        np.save(mean_file, mean_survival_ratios)
        np.save(std_file, std_survival_ratios)
    else:
        mean_survival_ratios = np.load(mean_file)
        std_survival_ratios = np.load(std_file)

    # Visualize results
    visualize_results(mean_survival_ratios, name='Mean', cmap='viridis')
    visualize_results(std_survival_ratios, name='STD', cmap='hot')