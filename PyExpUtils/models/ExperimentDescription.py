import json
import os
from PyExpUtils.utils.permute import getParameterPermutation, getNumberOfPermutations
from PyExpUtils.utils.dict import merge, hyphenatedStringify, pick
from PyExpUtils.utils.fp import memoize
from PyExpUtils.utils.str import interpolate
from PyExpUtils.models.Config import getConfig

class ExperimentDescription:
    def __init__(self, d, path=None, keys='metaParameters'):
        self._d = d
        self.keys = keys
        self.path = path

    def _getKeys(self, keys):
        keys = keys if keys is not None else self.keys
        return keys if isinstance(keys, list) else [keys]

    def permutable(self, keys='metaParameters'):
        keys = self._getKeys(keys)

        sweeps = {}
        for key in keys:
            sweeps[key] = self._d[key]

        return sweeps

    def getPermutation(self, idx, keys='metaParameters', Model=None):
        sweeps = self.permutable(keys)
        permutation = getParameterPermutation(sweeps, idx)
        d = merge(self._d, permutation)

        return Model(d) if Model else d

    @memoize
    def permutations(self, keys='metaParameters'):
        sweeps = self.permutable(keys)
        return getNumberOfPermutations(sweeps)

    @memoize
    def getRun(self, idx, keys='metaParameters'):
        count = self.permutations(keys)
        return idx // count

    @memoize
    def getExperimentName(self):
        cwd = os.getcwd()
        exp_dir = getConfig().experiment_directory

        if self.path is None:
            return self._d.get('name', 'unnamed')

        path = self.path \
            .replace(cwd + '/', '') \
            .replace(exp_dir + '/', '') \
            .replace('./', '')

        return '/'.join(path.split('/')[:-1])

    def interpolateSavePath(self, idx, permute='metaParameters', key = None):
        if key is None:
            config = getConfig()
            key = config.save_path

        params = pick(self.getPermutation(idx, permute), permute)
        param_string = hyphenatedStringify(params)

        run = self.getRun(idx, permute)

        special_keys = {
            'params': param_string,
            'run': str(run),
            'name': self.getExperimentName()
        }
        d = merge(self.__dict__, special_keys)

        return interpolate(key, d)

def loadExperiment(path, Model=ExperimentDescription):
    with open(path, 'r') as f:
        d = json.load(f)

    return Model(d, path=path)
