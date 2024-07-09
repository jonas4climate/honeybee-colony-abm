import numpy as np
import os

from mesa.batchrunner import batch_run
from multiprocessing import freeze_support

from src.model.config.SensitivityAnalysisConfig import SensitivityAnalysisConfig as SAC
from src.model.Model import ForagerModel
from src.model.config.HiveConfig import HiveConfig

# We define our variables and bounds
problem = {
    'num_vars': 2,
    'names': ['DEFAULT_INIT_NECTAR', 'N_BEES'],
    'bounds': [
            [SAC.HiveParamBounds.DEFAULT_INIT_NECTAR_MIN, SAC.HiveParamBounds.DEFAULT_INIT_NECTAR_MAX], 
            [SAC.HiveParamBounds.N_BEES_MIN, SAC.HiveParamBounds.N_BEES_MAX]
        ]
}

# Which data to actually collect from the model
DATA_COLLECTORS = ['Bee count 🐝', 'Hive stock 🍯', 'exploring 🗺️', 'carrying 🎒']

# Which of the parameters are integers
INTEGER_PARAMS = ['N_BEES']

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
N_ITERATIONS = 3    # TODO: Change to 16
N_STEPS = 50        # TODO: Change to 1000
N_SAMPLES = 8

# Container for storing data
DATA = np.zeros((len(problem['names']), N_SAMPLES * N_ITERATIONS, len(DATA_COLLECTORS) + 1))

# Data will be stored in this directory
SAVE_PATH = os.path.join('data', 'sensitivity_analysis', 'initial_conditions')

if __name__ == '__main__':
    freeze_support()
    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        if var not in INTEGER_PARAMS:
            samples = np.linspace(*problem['bounds'][i], num=N_SAMPLES)
        else:
            samples = np.linspace(*problem['bounds'][i], num=N_SAMPLES, dtype=int)
        
        results = batch_run(ForagerModel, 
                parameters={'hive_config': [HiveConfig(**{var:sample}) for sample in samples]},
                number_processes=8, 
                iterations=N_ITERATIONS, 
                max_steps=N_STEPS,
                display_progress=True)
        
        for (j, res) in enumerate(results):
            DATA[i, j, 0] = getattr(res['hive_config'], var)
            for (k, dc) in enumerate(DATA_COLLECTORS):
                DATA[i, j, k + 1] = res[dc]
        
        np.save(os.path.join(SAVE_PATH, var + ".npy"), DATA[i])
        