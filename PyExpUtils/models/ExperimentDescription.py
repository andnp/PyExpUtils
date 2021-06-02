from PyExpUtils.utils.arrays import unwrap
import json
import os
import PyExpUtils.utils.path as Path
from PyExpUtils.utils.permute import getParameterPermutation, getNumberOfPermutations
from PyExpUtils.utils.dict import merge, hyphenatedStringify, pick
from PyExpUtils.utils.str import interpolate
from PyExpUtils.models.Config import getConfig
from PyExpUtils.FileSystemContext import FileSystemContext

# type checking
from typing import Optional, Union, List, Dict, Any, Type
Keys = Union[str, List[str]]

"""doc
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
"""
class ExperimentDescription:
    def __init__(self, d: Dict[str, Any], path: Optional[str] = None, keys: Keys = 'metaParameters', save_key: Optional[str] = None):
        # the raw serialized json
        self._d = d
        # a collection of keys to permute over
        self.keys = keys
        # path to the experiment description file
        self.path = path
        # interpolation key for saving
        self.save_key = save_key

    # get the keys to permute over
    def getKeys(self, keys: Optional[Keys] = None):
        keys = keys if keys is not None else self.keys
        return keys if isinstance(keys, list) else [keys]

    def _getSaveKey(self, save_key: Optional[str] = None):
        if save_key is not None:
            return save_key

        if self.save_key is not None:
            return self.save_key

        config = getConfig()
        return config.save_path

    """doc
    Gives a list of parameters that can be swept over.

    Using above example dictionary:
    ```python
    params = exp.permutable()
    print(params) # -> { 'alpha': [1.0, 0.5, 0.25, 0.125], 'lambda': [1.0, 0.99, 0.98, 0.96] }
    ```
    """
    def permutable(self):
        keys = self.getKeys()

        sweeps: Dict[str, Any] = {}
        for key in keys:
            sweeps[key] = self._d[key]

        return sweeps

    """doc
    Gives the `i`'th permutation of sweepable parameters.
    Handles wrapping indices, so can perform multiple runs of the same parameter setting by setting `i` large.
    Returns the entire dictionary, not just the sub-dictionary containing the permutation.

    In the above dictionary, there are 16 total parameter permutations.
    ```python
    params = exp.getPermutation(0)
    print(params['metaParameters']) # -> { 'alpha': 1.0, 'lambda': 1.0 }

    params = exp.getPermutation(1)
    print(params['metaParameters']) # -> { 'alpha': 1.0, 'lambda': 0.99 }

    params = exp.getPermutation(15)
    print(params['metaParameters']) # -> { 'alpha': 0.125, 'lambda': 0.96 }

    params = exp.getPermutation(16)
    print(params['metaParameters']) # -> { 'alpha': 1.0, 'lambda': 1.0 }
    ```
    """
    def getPermutation(self, idx: int):
        sweeps = self.permutable()
        permutation = getParameterPermutation(sweeps, idx)
        d = merge(self._d, permutation)

        return d

    """doc
    Gives the total number of parameter permutations.

    ```python
    num_params = exp.numPermutations()
    print(num_params) # -> 16
    ```
    """
    def numPermutations(self):
        sweeps = self.permutable()
        return getNumberOfPermutations(sweeps)

    """doc
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
    """
    def getRun(self, idx: int):
        count = self.numPermutations()
        return idx // count

    """doc
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
    """
    def getExperimentName(self):
        cwd = os.getcwd()
        exp_dir = getConfig().experiment_directory

        if exp_dir is None:
            exp_dir = ''

        if self.path is None:
            return str(self._d.get('name', 'unnamed'))

        path = self.path \
            .replace(cwd + '/', '') \
            .replace(exp_dir + '/', '') \
            .replace('./', '')

        return Path.up(path)

    """doc
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
    """
    def interpolateSavePath(self, idx: int, key: Optional[str] = None):
        key = self._getSaveKey(key)

        permute = unwrap(self.getKeys())
        params = pick(self.getPermutation(idx), permute)
        param_string = hyphenatedStringify(params)

        run = self.getRun(idx)

        special_keys = {
            'params': param_string,
            'run': str(run),
            'name': self.getExperimentName()
        }
        d = merge(self.__dict__, special_keys)

        return interpolate(str(key), d)

    """doc
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
    """
    def buildSaveContext(self, idx: int, base: str = '', key: Optional[str] = None):
        path = self.interpolateSavePath(idx, key)
        return FileSystemContext(path, base)

"""doc
Loads an ExperimentDescription from a JSON file (preferred way to make ExperimentDescriptions).

```python
exp = loadExperiment('experiments/MountainCar-v0/sarsa.json')
```
"""
def loadExperiment(path: str, Model: Type[ExperimentDescription] = ExperimentDescription):
    with open(path, 'r') as f:
        d = json.load(f)

    return Model(d, path=path)
