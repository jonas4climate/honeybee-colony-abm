import numpy as np

from mesa.batchrunner import batch_run
from multiprocessing import freeze_support

from src.model.agents.BeeSwarm import BeeSwarm
from src.model.config.SensitivityAnalysisConfig import SensitivityAnalysisConfig as SAConfig
from src.model.Model import ForagerModel

# We define our variables and bounds
problem = {
    'num_vars': 2,
    'names': ['p_storm', 'storm_duration'],
    'bounds': [
            [SAConfig.P_STORM_MIN, SAConfig.P_STORM_MAX], 
            [SAConfig.STORM_DURATION_MIN, SAConfig.STORM_DURATION_MAX]
        ]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
N_ITERATIONS = 1 # TODO: Change
N_STEPS = 100
N_SAMPLES = 8

data = {}

if __name__ == '__main__':
    freeze_support()
    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=N_SAMPLES)
        
        # Keep in mind that wolf_gain_from_food should be integers. You will have to change
        # your code to acommodate for this or sample in such a way that you only get integers.
        if var == 'storm_duration':
            samples = np.linspace(*problem['bounds'][i], num=N_SAMPLES, dtype=int)
        
        results = batch_run(ForagerModel, 
                parameters={var: samples},
                number_processes=8, 
                iterations=N_ITERATIONS, 
                max_steps=N_STEPS,
                display_progress=True)
    
        print(results)
        
        