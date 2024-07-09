import numpy as np
import os

from mesa.batchrunner import batch_run
from multiprocessing import freeze_support

from src.model.config.SensitivityAnalysisConfig import SensitivityAnalysisConfig as SAC
from src.model.Model import ForagerModel, RunMode
from src.model.config.HiveConfig import HiveConfig

# Which data to actually collect from the model
DATA_COLLECTORS = ['Bee count 🐝', 'Hive stock 🍯', 'Foragers']

PARAMS = ['DEFAULT_INIT_NECTAR', 'N_BEES']

# Which of the parameters are integers
INTEGER_PARAMS = ['N_BEES']

# Data will be stored in this directory
SAVE_PATH = os.path.join('data', 'sensitivity_analysis', 'initial_conditions')

# We define our variables and bounds
PROBLEM = {
    'num_vars': 2,
    'names': PARAMS,
    'bounds': [
            [SAC.HiveParamBounds.DEFAULT_INIT_NECTAR_MIN, SAC.HiveParamBounds.DEFAULT_INIT_NECTAR_MAX], 
            [SAC.HiveParamBounds.N_BEES_MIN, SAC.HiveParamBounds.N_BEES_MAX]
        ]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
N_ITERATIONS = 8
N_STEPS = 500
N_SAMPLES = 8

# Container for storing data
DATA = np.zeros((len(PROBLEM['names']), N_SAMPLES * N_ITERATIONS, len(DATA_COLLECTORS) + 1))

if __name__ == '__main__':
    freeze_support()
    for i, var in enumerate(PROBLEM['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        if var not in INTEGER_PARAMS:
            samples = np.linspace(*PROBLEM['bounds'][i], num=N_SAMPLES)
        else:
            samples = np.linspace(*PROBLEM['bounds'][i], num=N_SAMPLES, dtype=int)
        
        params = {
            {'hive_config': [HiveConfig(**{var:sample}) for sample in samples]},
            {''}
        }

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
        