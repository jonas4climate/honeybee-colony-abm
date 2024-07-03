from mesa import  Model

import numpy as np
import matplotlib.pyplot as plt

from .Bee import BeeSwarm, BeeState
from .Model import Model
from .Hive import Hive
from .CustomScheduler import CustomScheduler

def bees_proportion(model):
    all_bees = model.get_agents_of_type(BeeSwarm)
    if all_bees:
        return {state.value: len([a for a in all_bees if a.state == state]) / len(all_bees) for state in BeeState}
    else:
        return {state.value: 0 for state in BeeState}

def nectar_in_hives(model):
    all_hives = model.get_agents_of_type(Hive)
    if all_hives:
        return [i.nectar for i in all_hives]
    else:
        raise Exception("No hives in the model")
    
def average_bee_fed(model):
    all_bees = model.get_agents_of_type(BeeSwarm)
    if all_bees:
        return np.mean([i.fed for i in all_bees])
    else:
        return 0

def mean_perceived_nectar(model: Model):
    all_bees = model.get_agents_of_type(BeeSwarm)
    if all_bees:
        return np.mean([b.perceived_nectar for b in all_bees])
    else:
        return 0
    
def get_bee_count(scheduler: CustomScheduler) -> int:
    return len(scheduler.all_agents[BeeSwarm].values())

def get_scent_scale(model: Model):
    all_bees = model.get_agents_of_type(BeeSwarm)
    if all_bees:
        return [b.scent_scale for b in all_bees]

def visualize_scent_scale(scent_scales):
    plt.figure()
    plt.hist(scent_scales)
    plt.xlabel("Scent scale")
    plt.ylabel("Number of bees")
    plt.title("Scent scale distribution of all bees")
    plt.show()