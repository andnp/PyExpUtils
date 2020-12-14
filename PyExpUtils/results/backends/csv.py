import numpy as np
from typing import Any, Callable, Dict, List, Optional, Type, Union
from PyExpUtils.utils.types import T
from PyExpUtils.results.indices import listIndices
from PyExpUtils.utils.csv import arrayToCsv, buildCsvHeader, buildCsvParams
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.utils.fp import once

class Result(BaseResult):
    def __init__(self, exp: ExperimentDescription, idx: int, result: List[Optional[List[str]]]):
        super().__init__('', exp, idx)
        self._raw = result
        self.data: Optional[Union[np.ndarray, List]] = None

    def load(self) -> Union[np.ndarray, List]:
        if self.data is None:
            clean = list(dropNones(self._raw))
            uneven = hasUnevenShape(clean)

            data: Union[List, np.ndarray] = []
            if uneven:
                warnShape()
                data = [ np.array(x, dtype='float32') for x in clean ]

            else:
                data = np.array(clean, dtype='float32')

            self.data = data

        return self.data

    def mean(self) -> np.ndarray:
        return np.mean(self.load(), axis=0)

    def stderr(self) -> np.ndarray:
        n = self.runs()
        return np.std(self.load(), axis=0, ddof=1) / np.sqrt(n)

    def runs(self):
        return len(self.load())


def hasUnevenShape(arr: List) -> bool:
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

# instead of scanning multiple passes through the CSV to find the lines corresponding to a certain set of parameters
# first take a single scanning pass and utilize the dictionary's hashing to build a map
#   ParameterPermutation -> List[results]
def buildResultDict(data: List[str], exp: ExperimentDescription):
    # figure out how many columns our header has
    # the first several CSV values in the row will be the parameter settings
    header = buildCsvHeader(exp)
    cols = len(header.split(','))

    out: Dict[str, List[Optional[List[str]]]] = {}

    # estimate how many runs each parameter setting should have
    expected_runs = int(np.ceil(len(data) / exp.numPermutations()))
    for line in data:
        # break the row into a list of cells
        parts = line.split(',')
        # grab the parameter settings as a comma-separated string
        key = ','.join(parts[:cols])
        # get the run number so we can reconstruct in order
        run = int(parts[cols])
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


def loadResults(exp: ExperimentDescription, filename: str, base: str = './', ResultClass: Type[Result] = Result):
    context = exp.buildSaveContext(0, base=base)
    with open(context.resolve(filename), 'r') as f:
        data = f.readlines()

    result_dict = buildResultDict(data, exp)

    for idx in listIndices(exp):
        key = buildCsvParams(exp, idx)
        result = result_dict.get(key)

        if result is None:
            print('Result not found: ', key)
            continue

        yield ResultClass(exp, idx, result)

def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: Any,  base: str = './', precision: Optional[int] = None):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-4:]:
        filename += '.csv'

    csv_file = save_context.resolve(f'{filename}')

    csv_data = arrayToCsv(data, precision=precision)
    csv_params = buildCsvParams(exp, idx)
    run = exp.getRun(idx)

    with open(csv_file, 'a+') as f:
        f.write(f'{csv_params},{run},{csv_data}\n')

    return csv_file
