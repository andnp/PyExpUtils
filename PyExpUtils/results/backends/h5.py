import h5py
import numpy as np
from PyExpUtils.results.indices import listIndices
from typing import Any, Dict, List, Sequence, Type, Union
from PyExpUtils.utils.cache import Cache
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.utils.csv import buildCsvParams
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class H5Result(BaseResult):
    def __init__(self, path: str, exp: ExperimentDescription, idx: int):
        super().__init__(path, exp, idx)

    def _load(self):
        f = h5py.File(self.path, 'r')
        key = buildCsvParams(self.exp, self.idx)

        group = f[key]
        num_runs = len(group)

        if num_runs == 0:
            print('Result not found: ', key)
            return

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
        if uneven:
            final_data = _padUneven(final_data, np.nan)

        f.close()

        return final_data

    def _default(self) -> np.ndarray:
        return np.zeros(0)

    def mean(self) -> np.ndarray:
        return np.nanmean(self.load(), axis=0)

    def runs(self):
        return len(self.load())

    def stderr(self) -> np.ndarray:
        return np.nanstd(self.load(), axis=0, ddof=1) / np.sqrt(self.runs())

def detectMissingIndices(exp: ExperimentDescription, runs: int, filename: str, base: str = './'):
    context = exp.buildSaveContext(0, base=base)
    path = context.resolve(filename)

    # try to open the file. If it doesn't exist, then assume that all results are missing
    try:
        f = h5py.File(path, 'r')
    except Exception:
        for idx in listIndices(exp):
            yield idx
        return

    params = exp.numPermutations()

    # loop over just the first run of indices to find the right file
    # then we will loop over secondary indices for this param setting
    for idx in listIndices(exp):
        key = buildCsvParams(exp, idx)

        # if we don't see this key at all, then all of the results for this param setting are missing
        if key not in f:
            for r in range(runs):
                yield idx + params * r

        # otherwise we need to check within this group for missing runs
        else:
            group = f[key]

            # before we dig into the data (which is costly), check if we can short-circuit out
            if len(group) == runs:
                continue

            for r in range(runs):
                if str(r) not in group:
                    yield idx + params * r

    f.close()


_result_cache = Cache[List[H5Result]]()

# TODO: consider if there is a meaningful cache that we can do here
def loadResults(exp: ExperimentDescription, filename: str, base: str = './', cache: bool = True, ResultClass: Type[H5Result] = H5Result):
    context = exp.buildSaveContext(0, base=base)
    path = context.resolve(filename)

    generator = (ResultClass(path, exp, idx) for idx in listIndices(exp))
    if cache:
        return _result_cache.get(path, lambda path: list(generator))

    return generator

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

        if sub is not None:
            final_file = saveResults(exp, inner_idx, filename, sub, base)

    return final_file

def _padUneven(data: Sequence[np.ndarray], val: float):
    lens = np.array([len(item) for item in data])
    mask = lens[:, None] > np.arange(lens.max())
    out = np.full(mask.shape, val)
    out[mask] = np.concatenate(data)
    return out
