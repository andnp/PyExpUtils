import h5py
import numpy as np
from PyExpUtils.results.indices import listIndices
from typing import Any, Dict, Sequence, Type, Union
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.utils.csv import buildCsvParams
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class H5Result(BaseResult):
    def __init__(self, path: str, exp: ExperimentDescription, idx: int, data: Any, uneven: bool = False):
        super().__init__(path, exp, idx)

        self._data = data

        if uneven:
            self._data = _padUneven(data, np.nan)

    def _load(self):
        if self._data is None:
            raise Exception('theoretically unreachable code')

        return self._data

    # in this case we can't lazy load, so this is just a pass-through
    def load(self):
        return self._load()

    def mean(self) -> np.ndarray:
        return np.nanmean(self.load(), axis=0)

    def runs(self):
        return self.load().shape[0]

    def stderr(self) -> np.ndarray:
        return np.nanstd(self.load(), axis=0, ddof=1) / np.sqrt(self.runs())

# TODO: consider if there is a meaningful cache that we can do here
def loadResults(exp: ExperimentDescription, filename: str, base: str = './', cache: bool = True, ResultClass: Type[H5Result] = H5Result):
    context = exp.buildSaveContext(0, base=base)
    path = context.resolve(filename)

    data = h5py.File(path, 'r')

    for idx in listIndices(exp):
        # use the parameter settings to get the group
        key = buildCsvParams(exp, idx)
        group = data[key]

        num_runs = len(group)

        if num_runs == 0:
            print('Result not found: ', key)
            continue

        # set up a placeholder for data that can hold run data
        # in order
        all_data: Dict[int, np.ndarray] = {}

        uneven = False
        length = -1

        # each dataset represents a single run
        # also check if the data is uneven length
        # if so, we will need to handle it specially later on
        for run in group:
            run_data = group[run][:]
            all_data[int(run)] = run_data

            if length == -1:
                length = run_data.shape[0]

            elif run_data.shape[0] != length:
                uneven = True

        # convert from dictionary to ordered list
        final_data = [all_data[run] for run in sorted(all_data.keys())]

        yield ResultClass(path, exp, idx, final_data, uneven)

    data.close()

def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './'):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-3:]:
        filename += '.h5'

    h5_file = save_context.resolve(filename)
    header = buildCsvParams(exp, idx)
    run = exp.getRun(idx)

    # h5py includes its own file-locking, no special handling need here
    with h5py.File(h5_file, 'a') as f:
        if header not in f:
            grp = f.create_group(header)
        else:
            grp = f[header]

        grp.create_dataset(str(run), data=data, compression='lzf')

    return h5_file

# TODO: instead of bootstrapping off of saveResults
# rewrite the logic here to be more efficient with file handles
def saveSequentialRuns(exp: ExperimentDescription, idx: int, filename: str, data: Union[Sequence[Any], np.ndarray], base: str = './'):
    params = exp.numPermutations()

    final_file = ''
    for run, sub in enumerate(data):
        inner_idx = params * run + idx

        final_file = saveResults(exp, inner_idx, filename, sub, base)

    return final_file

def _padUneven(data: Sequence[np.ndarray], val: float):
    lens = np.array([len(item) for item in data])
    mask = lens[:, None] > np.arange(lens.max())
    out = np.full(mask.shape, val)
    out[mask] = np.concatenate(data)
    return out
