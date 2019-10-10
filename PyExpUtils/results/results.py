import numpy as np
from PyExpUtils.results.paths import listResultsPaths
from PyExpUtils.utils.arrays import first
from PyExpUtils.utils.dict import equal

class Result:
    def __init__(self, path, exp, idx):
        self.path = path
        self.exp = exp
        self.idx = idx
        self.params = exp.getPermutation(idx)[exp._getKeys()[0]]
        self._data = None
        self._reducer = lambda m: m

    def _lazyLoad(self):
        if self._data is not None:
            return self._data

        try:
            self._data = np.load(self.path, allow_pickle=True)
            return self._data
        except:
            print('Result not found :: ' + self.path)
            return (np.NaN, np.NaN, 0)

    def reducer(self, lm):
        self._reducer = lm
        return self

    def mean(self):
        return self._reducer(self._lazyLoad()[0])

    def stderr(self):
        return self._reducer(self._lazyLoad()[1])

    def runs(self):
        return self._reducer(self._lazyLoad()[2])

def splitOverParameter(results, param):
    parts = {}
    for r in results:
        param_value = r.params[param]

        if param_value not in parts:
            parts[param_value] = []

        parts[param_value].append(r)

    return parts

def sliceOverParameter(results, slicer, param):
    parts = splitOverParameter(results, param)

    sl = {}
    for k in parts:
        sl[k] = find(parts[k], slicer, ignore=[param])

    return sl

def getBest(results, steps=None, percent=1.0, comparator=lambda a, b: a < b):
    low = first(results)
    if steps is None:
        steps = low.mean().shape[0]

    steps = int(steps * percent)

    for r in results:
        a = r.mean()
        b = low.mean()
        am = np.mean(a[0 - steps:])
        bm = np.mean(b[0 - steps:])
        if np.isnan(bm) or comparator(am, bm):
            low = r

    return low

def find(stream, other, ignore=[]):
    params = other.params
    for res in stream:
        if equal(params, res.params, ignore):
            return res

def whereParameterEquals(results, param, value):
    return filter(lambda r: r.params.get(param, value) == value, results)

def whereParameterGreaterEq(results, param, value):
    return filter(lambda r: r.params.get(param, value) >= value, results)

def loadResults(exp, result_file):
    for i, path in enumerate(listResultsPaths(exp)):
        summary_path = path + '/' + result_file
        yield Result(summary_path, exp, i)
