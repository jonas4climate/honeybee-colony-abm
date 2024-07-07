import numpy as np
import os
from multiprocess.pool import Pool
from tqdm import tqdm

from src.model.Model import ForagerModel
from src.model.config.ModelConfig import ModelConfig as MC
import src.model.util.ModelBuilder as ModelBuilder


N_REPEATS = 32
N_STEPS = 1000

P_STORMS = [0.0, 0.0025, 0.005, 0.0075, 0.01]
STORM_DURATIONS = [5, 10, 15, 20, 25, 30, 35]

DATA_BEE_COUNT = np.zeros((len(P_STORMS), len(STORM_DURATIONS), N_REPEATS, N_STEPS))
DATA_NECTAR = np.zeros((len(P_STORMS), len(STORM_DURATIONS), N_REPEATS, N_STEPS))
DATA_RECRUITED = np.zeros((len(P_STORMS), len(STORM_DURATIONS), N_REPEATS, N_STEPS))
DATA_EXPLORERS = np.zeros((len(P_STORMS), len(STORM_DURATIONS), N_REPEATS, N_STEPS))

BEE_COUNT_FILE = os.path.join('data', 'weather_effects', 'bee_count.npy')
NECTAR_FILE = os.path.join('data', 'weather_effects', 'nectar.npy')
RECRUITED_FILE = os.path.join('data', 'weather_effects', 'recruited.npy')
EXPLORERS_FILE = os.path.join('data', 'weather_effects', 'explorers.npy')

# Turn this off if you want to rerun the experiment and generate new data
LOAD_DATA = False

def run_simulation(params):
    p_storm, storm_duration = params

    # Instatiate the model
    model = ForagerModel(p_storm=p_storm, storm_duration=storm_duration)
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
        pbar = tqdm(total=len(P_STORMS)*len(STORM_DURATIONS)*N_REPEATS, desc='Progress:')
        with Pool() as pool:
            for (i, p_storm) in enumerate(P_STORMS):
                for (j, storm_duration) in enumerate(STORM_DURATIONS):

                    # Run the simulations in parallel
                    params_list = [(p_storm, storm_duration) for _ in range(N_REPEATS)]
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