import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from tqdm import tqdm
import os
from multiprocess.pool import Pool

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
step = mean_survival_ratios.shape[2] // resolution

fig, axs = plt.subplots(1, resolution, figsize=(18, 4.5), sharey='all')
images = []  # List to store all the images for the colorbar
for i, ax in enumerate(axs):
    slice_idx = i * step
    slice_data = mean_survival_ratios[:, :, slice_idx]
    img = ax.imshow(slice_data, cmap='viridis')  # Store the AxesImage object
    images.append(img)
    ax.set_title(f'abort probability (per min) = {p_abort_params[slice_idx]*MINUTE:.2f}', fontsize=11)
    ax.set_xlabel('storm probability (per hour)')
    ax.set_xticks(np.arange(resolution))
    ax.set_xticklabels([f'{p_storm*HOUR:.2f}' for p_storm in p_storm_params])
    if i == 0:
        ax.set_ylabel('distance from hive (in km)')
    ax.set_yticks(np.arange(resolution))
    ax.set_yticklabels([f'{dist_from_hive/1000:.2f}' for dist_from_hive in res_dist_from_hive_params])

# Create a colorbar for the last image object with all axes specified
fig.colorbar(images[-1], ax=axs, orientation='horizontal', fraction=.1)

plt.suptitle(f'Mean survival ratios as a function of resource distance, storm and abort probabilities after {t_steps*dt/DAY} day(s)')
plt.show()