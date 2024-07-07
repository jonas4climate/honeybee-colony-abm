import numpy as np
import os
from multiprocess.pool import Pool
from tqdm import tqdm

from src.model.config.ModelConfig import ModelConfig as MC

from src.model.Model import ForagerModel
import src.model.util.ModelBuilder as ModelBuilder

# Total number of batches where at each batch N_POOLS runs are simulated.
N_BATCHES = 32
# Number of multiprocessing pools at each batch.
N_POOLS = 8

# Number of simulation steps at each run.
N_STEPS = 1000

# Data arrays
DATA_BEE_COUNT = np.zeros((N_BATCHES * N_POOLS, N_STEPS))
DATA_NECTAR = np.zeros((N_BATCHES * N_POOLS, N_STEPS))
DATA_RECRUITED = np.zeros((N_BATCHES * N_POOLS, N_STEPS))
DATA_EXPLORERS = np.zeros((N_BATCHES * N_POOLS, N_STEPS))

# Data files
BEE_COUNT_FILE = os.path.join('data', 'baseline_dynamics', 'bee_count.npy')
NECTAR_FILE = os.path.join('data', 'baseline_dynamics', 'nectar.npy')
RECRUITED_FILE = os.path.join('data', 'baseline_dynamics', 'recruited.npy')
EXPLORERS_FILE = os.path.join('data', 'baseline_dynamics', 'explorers.npy')

# Turn this off if you want to rerun the experiment and generate new data
LOAD_DATA = True

def run_simulation(params):
    # Instatiate the model
    model = ForagerModel()
    for _ in range(MC.N_RESOURCES_DEFAULT):
        ModelBuilder.add_resource_in_distance(model, MC.RESOURCE_DISTANCE_DEFAULT)

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
        pbar = tqdm(total=N_BATCHES*N_POOLS, desc='Progress:')

        for j in range(N_BATCHES):
            with Pool() as pool:

                # Run the simulations in parallel
                params_list = [() for _ in range(N_POOLS)]
                data = pool.map(run_simulation, params_list)
                
                # Put the data into containers
                for (k, data_row) in enumerate(data):
                    DATA_NECTAR[j*N_POOLS + k] = data_row[0]
                    DATA_RECRUITED[j*N_POOLS + k] = data_row[1]
                    DATA_EXPLORERS[j*N_POOLS + k] = data_row[2]
                    DATA_BEE_COUNT[j*N_POOLS + k] = data_row[3]

                pbar.update(N_POOLS)

        pbar.close()

        # Save the data to files
        np.save(BEE_COUNT_FILE, DATA_BEE_COUNT)
        np.save(NECTAR_FILE, DATA_NECTAR)
        np.save(RECRUITED_FILE, DATA_RECRUITED)
        np.save(EXPLORERS_FILE, DATA_EXPLORERS)