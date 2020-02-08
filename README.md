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
*Config:*:
Experiment utility configuration file.
Specifies global configuration settings:
- *save_path*: directory where experimental results will be stored
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
"save_path": "results",
"log_path": "~/scratch/.logs",
"experiment_directory": "experiments"
}
```

*getConfig*:
Memoized global configuration loader.
Will read `config.json` from (only once) and return a Config object.
```python
config = getConfig()
print(config.save_path) # -> 'results'
```

## runner
### PyExpUtils/runner/Slurm.py
*hours*:
Takes an integer number of hours and returns a well-formated time string.
```python
time = hours(3)
print(time) # -> '2:59:59
```

*gigs*:
Takes an integer number of gigabytes and returns a well-formated memory string.
```python
memory = gigs(4)
print(memory) # -> '4G'
```

## results
## utils
