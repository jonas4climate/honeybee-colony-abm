import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
from SALib.sample.saltelli import sample
from continuous_model.Model import ForagerModel
from itertools import combinations
import mesa.batchrunner as mb
from SALib.analyze import sobol
from BatchRunnerMP import BatchRunnerMP

def create_data(problem, save, rep=3, steps=200, samples=5):
    # Get model reporters from model
    model_reporters = {'n_agents_existed': lambda mod: mod.n_agents_existed,
                'n_bees': lambda mod: mod.schedule.get_bee_count(),
                # 'weather_event': lambda mod: mod.get_weather,
                'prop_resting': lambda mod: mod.bees_proportion()["resting"],
                'prop_returning': lambda mod: mod.bees_proportion()["returning"],
                'prop_exploring': lambda mod: mod.bees_proportion()["exploring"],
                'prop_carrying': lambda mod: mod.bees_proportion()["carrying"],
                'prop_dancing': lambda mod: mod.bees_proportion()["dancing"],
                'prop_following': lambda mod: mod.bees_proportion()["following"],
                'hive_1': lambda mod: mod.nectar_in_hives()[0]}
                # 'hive_2': lambda mod: mod.nectar_in_hives()[1]}

    # Sample from data
    params_values = sample(problem, N=samples)

    batch_run = BatchRunnerMP(ForagerModel,
                              nr_processes=os.cpu_count(),
                              max_steps=steps,
                              variable_parameters={val:[] for val in problem['names']},
                              model_reporters=model_reporters,
                              display_progress=True)

    pbar = tqdm(total=len(params_values))
    count = 0
    for i in range(rep):
        for values in params_values:
            var_parameters = {}
            for i, name in enumerate(problem['names']):
                var_parameters[name] = values[i]
            batch_run.run_iteration(var_parameters, tuple(values), count)
            count += 1
            pbar.update(1)
        print(f"Repetition No. {i}")
    pbar.close()
    data = batch_run.get_model_vars_dataframe()
    data.to_csv(save)
    return data

def clean_data(data, save):
    all_df = []
    for i, row in data.iterrows():
        temp_df = row['step_data']
        temp_df['sample'] = row['Run']
        temp_df['hive_1'] = row['hive_1']
        temp_df['hive_2'] = row['hive_2']
        temp_df['n_bees'] = row['n_bees']
        temp_df['n_agents_existed'] = row['n_agents_existed']
        temp_df['step'] = temp_df.index
        temp_df['prop_resting'] = row['prop_resting']
        temp_df['prop_returning'] = row['prop_returning']
        temp_df['prop_exploring'] = row['prop_exploring']
        temp_df['prop_carrying'] = row['prop_carrying']
        temp_df['prop_dancing'] = row['prop_dancing']
        temp_df['prop_following'] = row['prop_following']
        all_df.append(temp_df.iloc[10:])

    combined_df = pd.concat(all_df)
    df_test = combined_df.copy(deep=True)
    df_sample = df_test.groupby(['sample'])[
                ['prop_resting','prop_returning','prop_exploring','prop_carrying','prop_dancing','prop_following',]].mean()

    df_sample = df_sample.reset_index()
    df_sample.to_csv(f'{save}\\clean_data.csv')

    return df_sample



# Analyze the data
def analyse(data, problem):

    Si_prop_resting = sobol.analyze(problem, data['prop_resting'].values, print_to_console=False,n_processors=os.cpu_count(),parallel=True)
    Si_prop_returning = sobol.analyze(problem, data['prop_returning'].values, print_to_console=False,n_processors=os.cpu_count(),parallel=True)
    Si_prop_exploring = sobol.analyze(problem, data['prop_exploring'].values, print_to_console=False,n_processors=os.cpu_count(),parallel=True)
    Si_prop_carrying = sobol.analyze(problem, data['prop_carrying'].values, print_to_console=False,n_processors=os.cpu_count(), parallel=True)
    Si_prop_dancing = sobol.analyze(problem, data['prop_dancing'].values, print_to_console=False,n_processors=os.cpu_count(), parallel=True)
    Si_prop_following = sobol.analyze(problem, data['prop_following'].values, print_to_console=False,n_processors=os.cpu_count(), parallel=True)
    return [Si_prop_resting, Si_prop_returning, Si_prop_exploring, Si_prop_carrying, Si_prop_dancing, Si_prop_following]

def plot_index(s, params, i, title=''):
    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

def plot_sensitivity_order(data,problem, new_path):

    for Si in data:
        # First order
        plot_index(Si, problem['names'], '1', 'First order sensitivity')
        plt.savefig(f'plots/sobol_first_{new_path}.png')

        # Second order
        plot_index(Si, problem['names'], '2', 'Second order sensitivity')
        plt.savefig(f'plots/sobol_second_{new_path}.png')

        # Total order
        plot_index(Si, problem['names'], 'T', 'Total order sensitivity')
        plt.savefig(f'plots\\sobol_total_{new_path}.png')




if __name__ == "__main__":
    SAVE = "D:\\ABM\\abm-project\\continuous_model\\sensitivity_analysis"
    import os
    # import numpy as np
    import warnings
    # from continuous_model.config import *
    warnings.filterwarnings('ignore')
    os.chdir(SAVE)
    groups = np.arange(os.cpu_count())
    problem = {
        'num_vars': 2,
        'names': ['clust_coeff'], #, 'n_resources'],
        'bounds': [[0.8, 0.9]],  #, [1,5]],
        'groups':[f"G{i}" for i in groups],
    }
    collected_df = []
    for i in range(5):
        each_df = create_data(problem, save = "03-07 data_iter_{}.csv".format(i), rep=1, steps=200, samples=1)
        collected_df.append(each_df)
    data = pd.concat(collected_df)
    print("Data Collected")
    # Save cleaned data
    # cleaned_data = clean_data(data, save={SAVE})
    # print("Data Cleaned")
    # # Analyze the data
    # Si = analyse(cleaned_data, problem)
    # print("Data Analysed")
    # # Plot the data
    # sensitivity_plot = plot_sensitivity_order(Si, problem, new_path="test")



