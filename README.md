# PyExpUtils

[![Test](https://github.com/andnp/PyExpUtils/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/andnp/PyExpUtils/actions/workflows/test.yml)

Short for python experiment utilities.
This is a collection of scripts and machine learning experiment management tools that I use whenever I have to use python.

For a more complete discussion on my organization patterns for research codebases, [look in the docs](docs/OrganizationPatterns.md).

## This lib
Maintaining a rigorous experiment structure can be labor intensive.
As such, I've automated out many of the common pieces that I use in my research.

### Parameter Permutations
Experiments are encoded within JSON files.
The JSON files should contain all of the information necessary to reproduce an experiment, including all parameters swept.
Each of the parameter sweep specifications leads to a set of parameter permutations.
Imagine the case where you are sweeping over 2 meta-parameters:
```json
{
    "metaParameters": {
        "alpha": [0.01, 0.02, 0.04],
        "epsilon": [0.1, 0.2, 0.3]
    }
}
```
Here there are 9 total possible permutations: `{alpha: 0.01, epsilon: 0.1}`, `{alpha: 0.01, epsilon: 0.2}`, ...

These are indexed by a single numeric value.
To run each permutation once, simply execute indices `i \in [0..8]`.
To run each permutation twice, multiply by 2: `i \in [0..17]`.
In general for `n` runs and `p` permutations: `i \in [0..(n*p - 1)]`.


## models
A collection of JSON serialization classes with associated utility methods.
### PyExpUtils/models/Config.py
**Config**:

Experiment utility configuration file.
Specifies global configuration settings:
 - *save_path*: directory format where experimental results will be stored
 - *log_path*: directory where log files will be saved (e.g. stacktraces during experiments)
 - *experiment_directory*: root directory where all of the experiment description files are located

The config file should be at the root level of the repository and should be named `config.json`.
```
.git
.gitignore
tests/
scripts/
src/
config.json
```

An example configuration file:
```json
{
    "save_path": "results/{name}/{environment}/{agent}/{params}",
    "log_path": "~/scratch/.logs",
    "experiment_directory": "experiments"
}
```


**getConfig**:

Memoized global configuration loader.
Will read `config.json` (only once) and return a Config object.
```python
config = getConfig()
print(config.save_path) # -> 'results'
```


### PyExpUtils/models/ExperimentDescription.py
**ExperimentDescription**:

Main workhorse class of the library.
Takes a dictionary desribing all configurable options of an experiment and serializes that dictionary.
Provides a set of utility methods to run parameter sweeps in parallel and for storing data during experiments.
```python
exp_dict = {
    'algorithm': 'SARSA',
    'environment': 'MountainCar',
    'metaParameters': {
        'alpha': [1.0, 0.5, 0.25, 0.125],
        'lambda': [1.0, 0.99, 0.98, 0.96]
    }
}
exp = ExperimentDescription(d)
```


**permutable**:

Gives a list of parameters that can be swept over.
Using above example dictionary:
```python
params = exp.permutable()
print(params) # -> { 'alpha': [1.0, 0.5, 0.25, 0.125], 'lambda': [1.0, 0.99, 0.98, 0.96] }
```


**getPermutation**:

Gives the `i`'th permutation of sweepable parameters.
Handles wrapping indices, so can perform multiple runs of the same parameter setting by setting `i` large.
In the above dictionary, there are 16 total parameter permutations.
```python
params = exp.getPermutation(0)
print(params) # -> { 'alpha': 1.0, 'lambda': 1.0 }
params = exp.getPermutation(1)
print(params) # -> { 'alpha': 1.0, 'lambda': 0.99 }
params = exp.getPermutation(15)
print(params) # -> { 'alpha': 0.125, 'lambda': 0.96 }
params = exp.getPermutation(16)
print(params) # -> { 'alpha': 1.0, 'lambda': 1.0 }
```


**numPermutations**:

Gives the total number of parameter permutations.
```python
num_params = exp.numPermutations()
print(num_params) # -> 16
```


**getRun**:

Get the run number based on wrapping the index.
This is a count of how many times we've wrapped back around to the same parameter setting.
```python
num = exp.getRun(0)
print(num) # -> 0
num = exp.getRun(12)
print(num) # -> 0
num = exp.getRun(16)
print(num) # -> 1
num = exp.getRun(32)
print(num) # -> 2
```


**getExperimentName**:

Returns the name of the experiment if stated in the dictionary: `{ 'name': 'MountainCar-v0', ... }`.
If not stated, will try to determine the name of the experiment based on the path to the JSON it is stored in (assuming experiments are stored in JSON files).
```python
path = 'experiments/MountainCar-v0/sarsa.json'
with open(path, 'r') as f:
    d = json.load(path)
exp = ExperimentDescription(d, path)
name = exp.getExperimentName()
print(name) # -> d['name'] if available, or 'MountainCar-v0' if not.
```


**interpolateSavePath**:

Takes a parameter index and generates a path for saving results.
The path depends on the configuration settings of the library (i.e. `config.json`).
Note this uses an opinionated formatting for save paths and parameter string representations.
The configuration file can specify ordering and high-level control over paths, but for more fine-tuned control over how these are saved, inherit from this class and overload this method.
`config.json`:
```json
{
    "save_path": "results/{name}/{environment}/{agent}/{params}"
}
```
```python
path = exp.interpolateSavePath(0)
print(path) # -> 'results/MountainCar-v0/SARSA/alpha-1.0_lambda-1.0'
```


**buildSaveContext**:

Builds a `FileSystemContext` utility object that contains the save path for experimental results.
```python
file_context = exp.buildSaveContext(0)
# make sure folder structure is built
file_context.ensureExists()
# get the path where results should be saved
path = file_context.resolve('returns.npy')
print(path) # -> '/results/MountainCar-v0/SARSA/alpha-1.0_lambda-1.0/returns.npy'
# save results
np.save(path, returns)
```


**loadExperiment**:

Loads an ExperimentDescription from a JSON file (preferred way to make ExperimentDescriptions).

```python
exp = loadExperiment('experiments/MountainCar-v0/sarsa.json')
```


## runner
### PyExpUtils/runner/Slurm.py
**hours**:

Takes an integer number of hours and returns a well-formatted time string.
```python
time = hours(3)
print(time) # -> '2:59:59
```


**gb**:

Takes an integer number of gigabytes and returns a well-formatted memory string.
```python
memory = gb(4)
print(memory) # -> '4G'
```


## results
### PyExpUtils/results/indices.py
**listIndices**:

Returns an iterator over indices for each parameter permutation.
Can specify a number of runs and will cycle over the permutations `runs` number of times.

```python
for i in listIndices(exp, runs=2):
    print(i, exp.getRun(i)) # -> "0 0", "1 0", "2 0", ... "0 1", "1 1", ...
```


## utils
