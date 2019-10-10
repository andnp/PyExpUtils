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

### API
#### models/ExperimentDescription
De-serializes the experiment description json files.
Holds a few utility functions for working with these datafiles.

This should be extended by a subclass that knows the exact fields in your datafile.
This class makes no strong assumptions about the datafile structure, though defaults to assuming that the meta-parameters are contained in a field called `metaParameters`.

```python
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class Experiment(ExperimentDescription):
    # takes a dictionary (raw json file)
    # and the path to that json file
    def __init__(self, d, path):
        super().__init__(d, path)
        # require the json file to specify an agent name
        self.agent = d['agent']
        # optionally check if the json file specifies the number of steps
        self.steps = d.get('steps', 1000)

def loadExperiment(path):
    with open(path, 'r') as f:
        d = json.load(f)

    return Experiment(d, path)
```

**getPermutation**: gets the parameter permutation for a single index.
```python
exp = loadExperiment(sys.argv[1])
permutation = exp.getPermutation(0)
# permutation is a raw dictionary exactly the same as `d` above
# except `metaParameters` has been replaced with single values (instead of sweeps)
```

**permutations**: gets the number of possible permutations for given datafile.
```python
exp = loadExperiment(sys.argv[1])
num_permutations = exp.permutations()
```

**getRun**: returns the run number for a given index.
This is based on the number of permutations and the index value.
```python
run_num = exp.getRun(idx=22)
# if there are 10 permutations, this would return run_num=3
```

**interpolateSavePath**: takes a save path "key" and builds a path based on experiment meta-data.
```python
# values in {} will be replaced based on experiment description
path_key = 'results/{name}/{algorithm}/{dataset}/{params}/{run}'
save_path = exp.interpolateSavePath(idx=0)

print(save_path) # results/overfit/ann/fashion_mnist/alpha-0.01_epsilon-0.01/0
```

#### results/paths
**listResultsPaths**: takes an experiment description and returns an iterable of each result path for each meta-parameter permutation and each run.
```python
for path in listResultsPaths(exp, runs = 10):
    print(path) # results/overfit/ann/fashion_mnist/alpha-0.01_epsilon-0.01/0
```

**listMissingResults**: takes an experiment description and returns an iterable of all of the missing results. This is extremely useful for running experiments on a cluster where jobs may time out, or nodes may fail due to environmental issues. This allows rerunning of only the failed experiments.
```python
for path in listMissingResults(exp, runs=10):
    print(path) # results/overfit/ann/fashion_mnist/alpha-0.02_epsilon-0.01/8
```
