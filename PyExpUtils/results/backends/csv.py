import numpy as np
import numpy.typing as npt
from filelock import FileLock
from typing import Any, Callable, Dict, List, Optional, Type
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.results.indices import listIndices
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.utils.arrays import npPadUneven
from PyExpUtils.utils.cache import Cache
from PyExpUtils.utils.csv import arrayToCsv, buildCsvHeader, buildCsvParams
from PyExpUtils.utils.fp import once

# if we get uneven length rows, then we can't convert to an ndarray
# so instead we have to store as a raw list
class Result(BaseResult):
    def __init__(self, exp: ExperimentDescription, idx: int, result: List[Optional[List[str]]]):
        super().__init__('', exp, idx)
        self._raw = result
        self.data: Optional[np.ndarray] = None
        self.uneven = False

    def load(self) -> np.ndarray:
        if self.data is None:
            clean = list(dropNones(self._raw))
            self.uneven = hasUnevenShape(clean)

            if self.uneven:
                warnShape()
                self.data = npPadUneven([ np.array(x, dtype='float32') for x in clean ], np.nan)

            else:
                self.data = np.array(clean, dtype='float32')

        return self.data

    def mean(self) -> np.ndarray:
        return np.nanmean(self.load(), axis=0)

    def stderr(self) -> np.ndarray:
        n = self.runs()
        return np.nanstd(self.load(), axis=0, ddof=1) / np.sqrt(n)

    def runs(self):
        return len(self.load())


def hasUnevenShape(arr: List[List[str]]) -> bool:
    expected = len(arr[0])
    for x in arr:
        if len(x) != expected:
            return True

    return False

def dropNones(arr: List[Optional[List[str]]]):
    for x in arr:
        if x is not None:
            yield x

warnShape: Callable[[], None] = once(lambda: print('WARN - uneven shapes detected'))

# ---------------------
# For loading csv files
# ---------------------

ResultDict = Dict[str, List[Optional[List[str]]]]

# instead of scanning multiple passes through the CSV to find the lines corresponding to a certain set of parameters
# first take a single scanning pass and utilize the dictionary's hashing to build a map
#   ParameterPermutation -> List[results]
def buildResultDict(data: List[str], exp: ExperimentDescription):
    # figure out how many columns our header has
    # the first several CSV values in the row will be the parameter settings
    header = buildCsvHeader(exp)
    cols = len(header.split(','))

    out: ResultDict = {}

    # estimate how many runs each parameter setting should have
    expected_runs = int(np.ceil(len(data) / exp.numPermutations()))
    for line in data:
        # break the row into a list of cells
        parts = line.split(',')
        # grab the parameter settings as a comma-separated string
        key = ','.join(parts[:cols])
        # get the run number so we can reconstruct in order
        # this might fail whenever there is an inconsistent number of columns
        try:
            run = int(parts[cols])
        except Exception:
            continue
        # grab whatever data is associated with this row
        values = parts[cols + 1:]

        # this is some madness to make mypy happy
        # python + types still has some way to go..
        default: List[Optional[List[str]]] = []
        default += [None] * expected_runs

        # if we already have data for this parameter setting, just modify that
        # otherwise use the default array
        arr = out.get(key, default)

        # extend the array to fit this run if necessary
        # if we have 100 runs of parameter setting A and only 10 runs of B
        # then our "expected_runs" will be 55 for each, which is clearly wrong
        if run >= len(arr):
            offset = run - len(arr) + 1
            arr += [None] * offset

        arr[run] = values
        out[key] = arr

    return out

_result_cache = Cache[ResultDict]()

def _getResultDict(path: str, exp: ExperimentDescription):
    with open(path, 'r') as f:
        data = f.readlines()

    return buildResultDict(data, exp)

def loadResults(exp: ExperimentDescription, filename: str, base: str = './', cache: bool = True, ResultClass: Type[Result] = Result):
    context = exp.buildSaveContext(0, base=base)
    path = context.resolve(filename)

    if cache:
        # need to do a little manipulation to make sure we don't exclusively rely on the path
        # as a uniquely identifying key
        key = f'{path} + {exp.permutable()}'

        # then we deconstruct the modification
        result_dict = _result_cache.get(key, lambda key: _getResultDict(key.split(' + ')[0], exp))
    else:
        result_dict = _getResultDict(context.resolve(filename), exp)

    for idx in listIndices(exp):
        key = buildCsvParams(exp, idx)
        result = result_dict.get(key)

        if result is None:
            print('Result not found: ', key)
            continue

        yield ResultClass(exp, idx, result)

def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: npt.ArrayLike, base: str = './', precision: Optional[int] = None):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-4:]:
        filename += '.csv'

    csv_file = save_context.resolve(f'{filename}')

    csv_data = arrayToCsv(data, precision=precision)
    csv_params = buildCsvParams(exp, idx)
    run = exp.getRun(idx)

    with FileLock(csv_file + '.lock'):
        with open(csv_file, 'a+') as f:
            f.write(f'{csv_params},{run},{csv_data}\n')

    return csv_file

def saveSequentialRuns(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './', precision: Optional[int] = None):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-4:]:
        filename += '.csv'

    csv_file = save_context.resolve(filename)
    lines = []

    start_run = exp.getRun(idx)
    csv_params = buildCsvParams(exp, idx)
    for r, d in enumerate(data):
        csv_data = arrayToCsv(d, precision)

        run = start_run + r
        lines.append(f'{csv_params},{run},{csv_data}\n')

    with FileLock(csv_file + '.lock'):
        with open(csv_file, 'a+') as f:
            f.writelines(lines)

    return csv_file
