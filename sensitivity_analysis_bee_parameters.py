import numpy as np
import os

from mesa.batchrunner import batch_run
from multiprocessing import freeze_support

from src.model.config.SensitivityAnalysisConfig import SensitivityAnalysisConfig as SAC
from src.model.Model import ForagerModel, RunMode
from src.model.config.BeeSwarmConfig import BeeSwarmConfig
from src.model.config.ModelConfig import ModelConfig

# Which data to actually collect from the model
DATA_COLLECTORS = ['Bee count 🐝', 'Hive stock 🍯', 'Foragers']

# Full list of parameters
PARAMS = ['FOV', 'FOOD_CONSUMPTION', 
          'SPEED_IN_HIVE', 'SPEED_FORAGING', 
          'RESTING_PERIOD', 'P_NECTAR_INSPECTION', 'P_NECTAR_COMMUNICATION', 
          'P_FOLLOW_WAGGLE_DANCE', 'EXPLORING_INCENTIVE', 'CARRYING_CAPACITY', 'P_ABORT', 
          'P_BIRTH', 'P_DEATH', 'DEATH_STORM_FACTOR']

GENERAL_PARAMS = ['FOV', 'FOOD_CONSUMPTION']
MOVEMENT_PARAMS = ['SPEED_IN_HIVE', 'SPEED_FORAGING']
IN_HIVE_BEHAVIOUR_PARAMS = ['RESTING_PERIOD', 'P_NECTAR_INSPECTION', 'P_NECTAR_COMMUNICATION',]
EXPLORATION_AND_RECRUITMENT_PARAMS = ['P_FOLLOW_WAGGLE_DANCE', 'EXPLORING_INCENTIVE', 'CARRYING_CAPACITY', 'P_ABORT']
BIRTH_AND_DEATH_PARAMS = ['P_BIRTH', 'P_DEATH', 'DEATH_STORM_FACTOR']

# Which of the parameters are integers
INTEGER_PARAMS = ['RESTING_PERIOD', 'EXPLORING_INCENTIVE']  # TODO:

# Data will be stored in this directory
SAVE_PATH = os.path.join('data', 'sensitivity_analysis', 'bee_parameters')

# We define our variables and bounds
PROBLEM = {
    'num_vars': 14,
    'names': PARAMS,
    'bounds': [
            [SAC.BeeParamBounds.FOV_MIN, SAC.BeeParamBounds.FOV_MAX],
            [SAC.BeeParamBounds.FOOD_CONSUMPTION_MIN, SAC.BeeParamBounds.FOOD_CONSUMPTION_MAX],
            [SAC.BeeParamBounds.SPEED_IN_HIVE_MIN, SAC.BeeParamBounds.SPEED_IN_HIVE_MAX],
            [SAC.BeeParamBounds.SPEED_FORAGING_MIN, SAC.BeeParamBounds.SPEED_FORAGING_MAX],
            [SAC.BeeParamBounds.RESTING_PERIOD_MIN, SAC.BeeParamBounds.RESTING_PERIOD_MAX],
            [SAC.BeeParamBounds.P_NECTAR_INSPECTION_MIN, SAC.BeeParamBounds.P_NECTAR_INSPECTION_MAX],
            [SAC.BeeParamBounds.P_NECTAR_COMMUNICATION_MIN, SAC.BeeParamBounds.P_NECTAR_COMMUNICATION_MAX],
            [SAC.BeeParamBounds.P_FOLLOW_WAGGLE_DANCE_MIN, SAC.BeeParamBounds.P_FOLLOW_WAGGLE_DANCE_MAX],
            [SAC.BeeParamBounds.EXPLORING_INCENTIVE_MIN, SAC.BeeParamBounds.EXPLORING_INCENTIVE_MAX],
            [SAC.BeeParamBounds.CARRYING_CAPACITY_MIN, SAC.BeeParamBounds.CARRYING_CAPACITY_MAX],
            [SAC.BeeParamBounds.P_ABORT_MIN, SAC.BeeParamBounds.P_ABORT_MAX],
            [SAC.BeeParamBounds.P_BIRTH_MIN, SAC.BeeParamBounds.P_BIRTH_MAX],
            [SAC.BeeParamBounds.P_DEATH_MIN, SAC.BeeParamBounds.P_DEATH_MAX],
            [SAC.BeeParamBounds.DEATH_STORM_FACTOR_MIN, SAC.BeeParamBounds.DEATH_STORM_FACTOR_MAX]
        ]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
N_ITERATIONS = 8 # TODO: Change to 32
N_STEPS = 100   # TODO: Change to 1000
N_SAMPLES = 8

# Container for storing data
DATA = np.zeros((len(PROBLEM['names']), N_SAMPLES * N_ITERATIONS, len(DATA_COLLECTORS) + 1))

if __name__ == '__main__':
    freeze_support()
    for i, var in enumerate(PROBLEM['names']):
        # Get the bounds for this variable and get N_SAMPLES uniform samples within this space
        if var not in INTEGER_PARAMS:
            samples = np.linspace(*PROBLEM['bounds'][i], num=N_SAMPLES)
        else:
            samples = np.linspace(*PROBLEM['bounds'][i], num=N_SAMPLES, dtype=int)
        
        params = {
            'bee_config': [BeeSwarmConfig(**{var:sample}) for sample in samples],
            'run_mode': RunMode.SENSITIVITY_ANALYSIS,
            'n_resources': ModelConfig().N_RESOURCES_DEFAULT,
            'resource_dist': ModelConfig().RESOURCE_DISTANCE_DEFAULT
        }

        results = batch_run(ForagerModel, 
                parameters=params,
                number_processes=8, 
                iterations=N_ITERATIONS, 
                max_steps=N_STEPS,
                display_progress=True)
        
        for (j, res) in enumerate(results):
            DATA[i, j, 0] = getattr(res['bee_config'], var)
            for (k, dc) in enumerate(DATA_COLLECTORS):
                DATA[i, j, k + 1] = res[dc]
        
        np.save(os.path.join(SAVE_PATH, var + ".npy"), DATA[i])
        