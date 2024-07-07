import numpy as np
import os
from multiprocess.pool import Pool
from tqdm import tqdm

from src.model.Model import ForagerModel
import src.model.util.ModelBuilder as ModelBuilder


N_REPEATS = 32
N_STEPS = 1000

DIST_RESOURCES = np.linspace(30, 80, 6)
N_RESOURCES = [1, 2, 3, 4, 5, 6]

DATA_BEE_COUNT = np.zeros((len(DIST_RESOURCES), len(N_RESOURCES), N_REPEATS, N_STEPS))
DATA_NECTAR = np.zeros((len(DIST_RESOURCES), len(N_RESOURCES), N_REPEATS, N_STEPS))
DATA_RECRUITED = np.zeros((len(DIST_RESOURCES), len(N_RESOURCES), N_REPEATS, N_STEPS))
DATA_EXPLORERS = np.zeros((len(DIST_RESOURCES), len(N_RESOURCES), N_REPEATS, N_STEPS))

BEE_COUNT_FILE = os.path.join('data', 'resource_scarcity', 'bee_count.npy')
NECTAR_FILE = os.path.join('data', 'resource_scarcity', 'nectar.npy')
RECRUITED_FILE = os.path.join('data', 'resource_scarcity', 'recruited.npy')
EXPLORERS_FILE = os.path.join('data', 'resource_scarcity', 'explorers.npy')

# Turn this off if you want to rerun the experiment and generate new data
LOAD_DATA = True

def run_simulation(params):
    n_resource, resource_dist = params
    # Instatiate the model
    model = ForagerModel()
    for _ in range(n_resource):
        ModelBuilder.add_resource_in_distance(model, resource_dist)

    # Run the model
    for _ in range(N_STEPS):
        model.step()

    # Collect data
    dataframe = model.datacollector.get_model_vars_dataframe()
    
    nectar = dataframe['Hive stock 🍯'].to_numpy()
    recruited = dataframe['following 🎯'].to_numpy()
    explorers = dataframe['exploring 🗺️'].to_numpy()
    bee_count = dataframe['Bee count 🐝'].to_numpy()

    return nectar, recruited, explorers, bee_count

if __name__ == '__main__':
    if not LOAD_DATA:
        pbar = tqdm(total=len(N_RESOURCES)*len(DIST_RESOURCES)*N_REPEATS, desc='Progress:')
        with Pool() as pool:
            for (i, n_res) in enumerate(N_RESOURCES):
                for (j, dist_res) in enumerate(DIST_RESOURCES):

                    # Run the simulations in parallel
                    params_list = [(n_res, dist_res) for _ in range(N_REPEATS)]
                    data = pool.map(run_simulation, params_list)
                    
                    # Put the data into containers
                    for (k, data_row) in enumerate(data):
                        DATA_NECTAR[i,j,k] = data_row[0]
                        DATA_RECRUITED[i,j,k] = data_row[1]
                        DATA_EXPLORERS[i,j,k] = data_row[2]
                        DATA_BEE_COUNT[i,j,k] = data_row[3]

                    pbar.update(N_REPEATS)
                    
        pbar.close()

        # Save the data to files
        np.save(BEE_COUNT_FILE, DATA_BEE_COUNT)
        np.save(NECTAR_FILE, DATA_NECTAR)
        np.save(RECRUITED_FILE, DATA_RECRUITED)
        np.save(EXPLORERS_FILE, DATA_EXPLORERS)