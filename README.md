# PyExpUtils

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
Will read `config.json` from (only once) and return a Config object.
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

Takes an integer number of hours and returns a well-formated time string.
```python
time = hours(3)
print(time) # -> '2:59:59
```


**gigs**:

Takes an integer number of gigabytes and returns a well-formated memory string.
```python
memory = gigs(4)
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


**listMissingResults**:

Returns an iterator over indices which are missing results.
Detects if a results is missing by checking if the results folder exists, but cannot check the contents of the results folder.
If deeper checking is necessary, copy and modify the source of this function accordingly.

Useful for rescheduling jobs that were cancelled due to timeout (or randomly dropped jobs, etc.).
If no results are missing, then iterator is empty and the for loop is skipped.

```python
for i in listMissingResults(exp, runs=100):
    print(i) # -> 0, 1, 4, 23, 1002, ...
```


### PyExpUtils/results/results.py
**Result**:

The `Result` objects allows performing operations over results lazily so that many file system calls can be avoided.
This is extremely useful when doing large parameter sweeps and plotting over slices of parameters.
The object stores some metadata about the result that can be inferred from the experiment description without needing to open the result file.

```python
results = loadResults(exp, 'returns.npy') # -> gives an iterator over Result objects

for result in results:
    print(result.path) # -> 'results/MountainCar-v0/SARSA/alpha-1.0_lambda-1.0/returns.npy'
    print(result)

# only load results from disk where alpha > 0.2
results = filter(lambda res: res.params['alpha'] > 0.2, results)
for result in results:
    plot(result.load())

```


**reducer**:

Takes a function that manipulates the result data.
For example: useful for truncating data or looking at only final performance, etc.
```python
def getFirstNSteps(results, n):
    for result in results:
        yield result.reducer(lambda data: data[0:n])
results = loadResults(exp, 'returns.npy')
results = getFirstNSteps(results, 100)
```


**load**:

Load the result from disk.
The contents of the results file are cached, so as long as this result file is accessible (e.g. not garbage collected) you will only hit the filesystem once.
This is important for distributed filesystems (like on computecanada) where filesystem calls are extremely expensive.
Note that if the result does not exist (e.g. compute canada job timed out), then an error message will be printed but no exception will be thrown.
This way plotting code can still continue to run with partial results.


**ResultView**:

A "window" over a `Result` object that allows changing the type of reducer on the object while still referencing the same memory cache.
Useful for applying different views at the same results file without needing to load multiple copies of the result into memory or making multiple filesystem calls.
Returned from the `Result.reducer` method.
Maintains same API as a `Result` object and can be used interchangeably.

```python
results = loadResults(exp, 'returns.npy')
for result in results:
    view = result.reducer(lambda m: m.mean())
    view2 = result.reducer(lambda m: m.std())
```


**splitOverParameter**:

Utility function for sorting results into bins based on values of a metaParameter.
Does not load results from disk.

```python
results = loadResults(exp, 'returns.npy')
bins = splitOverParameter(results, 'alpha')
print(bins) # -> { 1.0: [Result, Result, ...], 0.5: [Result, Result, ...], 0.25: [Result, Result, ...], ...}
```


**sliceOverParameter**:

Utility function for sorting results by fixing all parameters except one, and returning a list of results for all other values of the other parameter.
Takes the list of results to consider, a result whose parameter values you want to match, and the name of the parameter you want to sweep over.
Does not load results from disk.

```python
results = loadResults(exp, 'returns.npy')
result = next(results)
slice = sliceOverParameter(results, result, 'lambda')

print(slice) # => { 1.0: [Result, Result, ...], 0.99: [Result, Result, ...], 0.98: [Result, Result], ....}
```


**getBest**:

Returns the best result over a list of results.
Can defined "best" based on the `comparator` option; defaults to returning smallest result (e.g. smallest error).
Can also find best result over a range of a learning curve by specifying the last n steps with `steps=n` or the last p percent of steps with `percent=p`; defaults to returning mean over whole learning curve.
**Requires loading all results in list from disk.**

```python
results = loadResults(exp, 'returns.npy')

# get the largest return over the last 10% of steps
best = getBest(results, percent=0.1, comparator=lambda a, b: a > b)
print(best.params) # -> { 'alpha': 1.0, 'lambda': 0.99 }

results = loadResults(exp, 'rmsve.npy')

# get the lowest rmsve over all steps
best = getBest(results)
print(best.params) # -> { 'alpha': 0.25, 'lambda': 1.0 }
```


**find**:

Find a specific result based on the metaParameters of another result.
Can optionally specify a list of parameters to ignore using for example `ignore=['alpha']`.
Will return the first result that matches.
Does not require loading results from disk.

```python
results = loadResults(exp, 'returns.npy')

result = next(results)
match = find(results, result, ignore=['lambda'])

print(result.params) # -> { 'alpha': 1.0, 'lambda': 1.0 }
print(match.params) # -> { 'alpha': 1.0, 'lambda': 0.98 }
```


**whereParameterEquals**:

Utility method for filtering results based on the value of a particular parameter.
If the listed parameter does not exist for some of the results (e.g. when comparing TD vs. GTD where TD does not have the second stepsize param), then those results will match True for the comparator.
Does not require loading results from disk.

```python
results = loadResults(exp, 'returns.npy')
results = whereParameterEquals(results, 'alpha', 0.25)

for res in results:
    print(res.params) # -> { 'alpha': 0.25, 'lambda': ... }
```


**whereParameterGreaterEq**:

Utility method for filtering results based on the value of a particular parameter.
If the listed parameter does not exist for some of the results (e.g. when comparing TD vs. GTD where TD does not have the second stepsize param), then those results will match True for the comparator.
Does not require loading results from disk.

```python
results = loadResults(exp, 'returns.npy')
results = whereParameterGreaterEq(results, 'alpha', 0.25)

for res in results:
    print(res.params) # -> { 'alpha': 0.25, 'lambda': ... }, { 'alpha': 0.5, 'lambda': ... }, ...
```


**loadResults**:

Returns an iterator over all results that are expected to exist given a particular experiment.
Takes the `ExperimentDescription` and the name of the result file.
Does not load results from disk.

```python
results = loadResults(exp, 'returns.npy')

for result in results:
    print(result) # -> `<Result>`
```


## utils
