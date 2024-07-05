# Beehive ABM
Agent-based modelling project and complexity analysis for Agent-based Models class (2024) @ UvA
<!-- 
## Setup

Ideally, set up the environment using `conda` (see [anaconda](https://www.anaconda.com/) or [miniconda](https://docs.anaconda.com/miniconda/)) via the `environment.yml` file by opening a terminal instance and running `conda env create -f environment.yml`. Then run `conda activate abm-bees`.

## Getting Started

After setup, move into the web server directory `continous_model` and run `python run.py` to start the web server GUI.

<br/> -->

## Repository structure

This repository has the following file structure:

* `data` folder contains pre-generated data used in our experiments
* `figures` folder contains plots and graphs used in our work and generated from the experimental data
* `src` folder contains all of the source code files
  * `model` folder contains source code relating to our Forager Dynamics Agent-based model
    * `agents` folder contains `.py` files corresponding to three types of agents used in the model: `Beeswarm`, `Hive` and `Resource` and implementing Mesa's [Agent](https://mesa.readthedocs.io/en/latest/_modules/mesa/agent.html#Agent) class
    * `config` folder contains all the constants and default parameter values used in the simulations
      * `BeeswarmConfig.py`, `HiveConfig.py` and `ResourceConfig.py` define constants and default parameters for three types of agents, accordingly
      * `ModelConfig.py` defines additional, global model constants 
      * `VisualConfig.py` contains constants used in JS server visualization
    * `util` folder contains additional utility files that did not fit anywhere else
    * `Model.py` contains the baseline logic of the model itself implementing Mesa's [Model](https://mesa.readthedocs.io/en/latest/_modules/mesa/model.html#Model) class
  * `server` **(TODO: this is wrong for now)** folder contains files related to JS server visualization (see below)

## JS server visualization

Mesa's [visualization module](https://mesa.readthedocs.io/en/latest/apis/visualization.html) provides functionality for animated simulation of the model. To run the simulation, open the terminal in the root directory of this repo and run `mesa runserver`. This starts the `run.py` file, which opens the server defined in `server.py`. Files `simple_continuous_canvas.js` and `SimpleContinuousModule.py` are used to visualize Mesa's [ContinuousSpace](https://mesa.readthedocs.io/en/latest/apis/space.html#mesa.space.ContinuousSpace) grid.

## Reproducing the experiments

Experiments described in our work are located in `experiments.ipynb` Jupyter Notebook file. Simply rerun the notebook to recreate the experiments. Keep in mind, however, that running all simulations can take a couple of hours / days depending on your machine. By default, the Notebook will load pre-generated data from `data` directory. This can be turned of within the notebook itself.