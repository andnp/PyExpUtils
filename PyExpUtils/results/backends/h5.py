import h5py
import numpy as np
from numba.typed import List as NList
from filelock import FileLock
from PyExpUtils.results.indices import listIndices
from typing import Any, Dict, List, Sequence, Type, Union, cast
from PyExpUtils.utils.cache import Cache
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.utils.csv import buildCsvParams
from PyExpUtils.utils.jit import try2jit
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
            # convert to np array
            run_data = np.asarray(group[run])
            all_data[int(run)] = run_data

            # if the data is scalar, no need to check shapes
            if np.ndim(run_data) == 0:
                continue

            if length == -1:
                length = run_data.shape[0]

            elif run_data.shape[0] != length:
                uneven = True

        # convert from dictionary to ordered list
        final_data = NList([all_data[run] for run in sorted(all_data.keys())])
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
        for idx in listIndices(exp, runs):
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
        return (_ for _ in _result_cache.get(path, lambda path: list(generator)))

    return generator

def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './'):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-3:]:
        filename += '.h5'

    h5_file = save_context.resolve(filename)
    header = buildCsvParams(exp, idx)
    run = exp.getRun(idx)

    # check if the data is a scalar. If so, compression cannot be used
    # Note: types are incorrect on grp.create_dataset, so a cast is necessary
    is_scalar = np.ndim(data) == 0
    compression = cast(str, None if is_scalar else 'lzf')

    # h5py's file-locking does not appear to work well
    with FileLock(h5_file + '.lock'):
        with h5py.File(h5_file, 'a') as f:
            if header not in f:
                grp = f.create_group(header)
            else:
                grp = f[header]

            grp.create_dataset(str(run), data=data, compression=compression)

    return h5_file

def saveSequentialRuns(exp: ExperimentDescription, idx: int, filename: str, data: Union[Sequence[Any], np.ndarray], base: str = './'):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-3:]:
        filename += '.h5'

    h5_file = save_context.resolve(filename)
    header = buildCsvParams(exp, idx)

    start_run = exp.getRun(idx)
    with FileLock(h5_file + '.lock'):
        with h5py.File(h5_file, 'a') as f:
            if header not in f:
                grp = f.create_group(header)
            else:
                grp = f[header]

            for r, d in enumerate(data):
                if d is None: continue

                is_scalar = np.ndim(d) == 0
                compression = cast(str, None if is_scalar else 'lzf')

                run = start_run + r
                grp.create_dataset(str(run), data=d, compression=compression)

    return h5_file

@try2jit
def _padUneven(data: Sequence[np.ndarray], val: float):
    m = max([len(sub) for sub in data])
    out = np.full((len(data), m), val)

    for i, sub in enumerate(data):
        out[i, :len(sub)] = sub

    return out
