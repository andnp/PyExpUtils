# Getting Started

To install this package using pip:
```bash
pip install git+ssh://git@github.com/andnp/PyExpUtils@2.11
```

An example with json description files:
```python
import json
from typing import Any, Dict
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

# Expects json files structured like:
"""
{
    "agent": "TDRC",
    "problem": "BairdsCounterexample",
    "metaParameters": {
        "alpha": [0.01, 0.02, 0.04],
        "lambda": [0.99, 0.98, 0.95, 0.9]
    }
}
"""
# The dependency on a `metaParameters` object is implicit due to the `ExperimentDescription` parent class.

class ExperimentModel(ExperimentDescription):
    def __init__(self, d: Dict[str, Any], path: str):
        super().__init__(d, path)

        # expect that the dictionary specifies the name of an agent
        self.agent: str = d['agent']
        # expect that the dictionary specifies the name of a problem
        self.problem: str = d['problem']

def load(path: str):
    with open(path, 'r') as f:
        # any type of file that can generate a dictionary is appropriate
        # this could be xml, json, yaml, whatever
        d = json.load(f)

    exp = ExperimentModel(d, path)
    return exp
```

Once you have defined the expected shape of the experiment description for your repo, you can define a complete experiment which quits early if data already exists, or saves data to file if not.
```python
import sys
import ExperimentModel

# assume this process is started like:
# python src/main.py path/to/description.json
# also assume that description.json file contains the example json in the above codeblock
exp = ExperimentModel.load(sys.argv[1])

# the parameter index
idx = 0

print(exp.numPermutations()) # -> 12

# to get a single parameter permutation
params = exp.getPermutation(idx)
print(params) # ->
"""
{
    "agent": "TDRC",
    "problem": "BairdsCounterexample",
    "metaParameters": {
        "alpha": 0.01,
        "lambda": 0.99
    }
}
"""

# check if there already exists data for this experiment
# assume the data is stored in h5 format
from PyExpUtils.results.backends.h5 import detectMissingIndices
missing = detectMissingIndices(exp, runs=1, filename='results.h5')

# if we already have data for this parameter and run, then just quit
if idx not in missing:
    exit()

agent = TDRC(params=params['metaParameters'])
problem = Bairds()

# assume this is a numpy array or a scalar
result = runExperiment(agent, problem)

# save the results to file
from PyExpUtils.results.backends.h5 import saveResults
saveResults(exp, idx, 'results.h5', result)
```
