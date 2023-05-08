from collections import defaultdict
import os
import glob
import pandas as pd
from filelock import FileLock
from typing import Any, Dict, Optional, Sequence, Union
from PyExpUtils.FileSystemContext import FileSystemContext
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.indices import listIndices
from PyExpUtils.results.tools import subsetDF
from PyExpUtils.utils.Collector import Collector
from PyExpUtils.utils.dict import flatKeys, get
from PyExpUtils.utils.types import NpList
from PyExpUtils.utils.asyncio import threadMap

class NoResultException(Exception):
    ...

def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: NpList, base: str = './', batch_size: Optional[int] = 20000):
    context = exp.buildSaveContext(idx, base=base)
    context.ensureExists()

    params = exp.getPermutation(idx)['metaParameters']
    header = getHeader(exp)
    pvalues = [get(params, k) for k in header]

    run = exp.getRun(idx)

    df = pd.DataFrame([pvalues + [run] + list(data)])

    # --------------
    # -- batching --
    # --------------
    data_file = _batchFile(context, filename, idx, batch_size)

    with FileLock(data_file + '.lock'):
        df.to_csv(data_file, mode='a+', header=False, index=False)

    return data_file

def saveSequentialRuns(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './', batch_size: Optional[int] = 20000):
    context = exp.buildSaveContext(idx, base=base)
    context.ensureExists()

    params = exp.getPermutation(idx)['metaParameters']
    header = getHeader(exp)
    pvalues = [get(params, k) for k in header]

    run = exp.getRun(idx)
    rows = []
    for i in range(len(data)):
        if data[i] is None:
            continue

        rows.append(pvalues + [run + i] + list(data[i]))

    df = pd.DataFrame(rows)

    # --------------
    # -- batching --
    # --------------
    data_file = _batchFile(context, filename, idx, batch_size)

    with FileLock(data_file + '.lock'):
        df.to_csv(data_file, mode='a+', header=False, index=False)

    return data_file

def saveCollector(exp: ExperimentDescription, collector: Collector, base: str = './', batch_size: Optional[int] = 20000, keys: Optional[Sequence[str]] = None):
    context = exp.buildSaveContext(0, base=base)
    context.ensureExists()

    header = getHeader(exp)

    to_write = defaultdict(list)

    if keys is None:
        keys = list(collector.keys())

    for filename in keys:
        for idx in collector.indices(filename):
            data = collector.get(filename, idx)

            params = exp.getPermutation(idx)['metaParameters']
            run = exp.getRun(idx)
            pvalues = [get(params, k) for k in header]

            row = pvalues + [run] + list(data)
            data_file = _batchFile(context, filename, idx, batch_size)

            to_write[data_file].append(row)

    for path in to_write:
        df = pd.DataFrame(to_write[path])

        with FileLock(path + '.lock'):
            df.to_csv(path, mode='a+', header=False, index=False)


def loadResults(exp: ExperimentDescription, filename: str, base: str = './', use_cache: bool = True) -> Union[pd.DataFrame, None]:
    context = exp.buildSaveContext(0, base=base)

    files = glob.glob(context.resolve(f'{filename}.*.csv'))

    # this could be because we did not use batching
    # try again without batching
    if len(files) == 0:
        files = glob.glob(context.resolve(f'{filename}.csv'))

    # if still no files, then no results exist
    if len(files) == 0:
        return None

    # get latest modification time
    times = (os.path.getmtime(f) for f in files)
    latest = max(*times, 0, 0)

    cache_file = context.resolve(filename + '.pkl')
    if use_cache and os.path.exists(cache_file) and os.path.getmtime(cache_file) > latest:
        df = pd.read_pickle(cache_file)
        return _subsetDFbyExp(df, exp)

    header = getHeader(exp)

    if len(files) == 0:
        raise NoResultException('No result files found')

    partials = threadMap(_readUnevenCsv, files)
    df = pd.concat(partials, ignore_index=True)

    nparams = len(header) + 1
    new_df = df.iloc[:, :nparams]
    new_df.columns = header + ['run']
    new_df['data'] = df.iloc[:, nparams:].values.tolist()

    if use_cache:
        new_df.to_pickle(cache_file)

    return _subsetDFbyExp(new_df, exp)


def detectMissingIndices(exp: ExperimentDescription, runs: int, filename: str, base: str = './'): # noqa: C901
    indices = listIndices(exp)
    nperms = exp.numPermutations()
    header = getHeader(exp)

    df = loadResults(exp, filename, base=base)
    # ----------------------------------
    # -- first case: no existing data --
    # ----------------------------------
    if df is None:
        for idx in indices:
            for run in range(runs):
                yield idx + run * nperms

        return

    grouped = df.groupby(header)
    for idx in indices:
        params = exp.getPermutation(idx)['metaParameters']
        pvals = tuple(get(params, k) for k in header)

        # get_group cannot handle singular tuples
        if len(pvals) == 1:
            pvals = pvals[0]

        # ------------------------------------
        # -- second case: no existing group --
        # ------------------------------------
        assert grouped is not None
        try:
            group = grouped.get_group(pvals)
        except KeyError:
            for run in range(runs):
                yield idx + run * nperms

            continue

        # -------------------------------------------------
        # -- final case: have data and group. check runs --
        # -------------------------------------------------
        for run in range(runs):
            if not (group['run'] == run).any():
                yield idx + run * nperms

def getHeader(exp: ExperimentDescription):
    params = exp.getPermutation(0)['metaParameters']
    keys = flatKeys(params)
    return sorted(keys)

def getParamValues(exp: ExperimentDescription, idx: int, header: Optional[Sequence[str]] = None):
    if header is None:
        header = getHeader(exp)

    params = exp.getPermutation(idx)['metaParameters']
    return [get(params, k) for k in header]

# ---------------
# -- Utilities --
# ---------------

# makes sure the dataframe only contains the data for a given experiment description
def _subsetDFbyExp(df: pd.DataFrame, exp: ExperimentDescription):
    params = exp._d['metaParameters']
    return subsetDF(df, _flattenKeys(params))

def _flattenKeys(d: Dict[str, Any]):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for sk, sv in _flattenKeys(v).items():
                out[f'{k}.{sk}'] = sv

        # if we have a list of objects, keep digging
        elif isinstance(v, list) and isinstance(v[0], dict):
            for i, sv in enumerate(v):
                for sk, ssv in _flattenKeys(sv).items():
                    out[f'{k}.[{i}].{sk}'] = ssv

        else:
            out[k] = v

    return out


# if the csv contains ragged rows (i.e. rows have different numbers of columns)
# then the native csv reader needs to know the max number of columns.
# the resulting df will have NaNs for the shorter rows
def _readUnevenCsv(f: str):
    with open(f, 'r') as temp_f:
        col_count = ( len(l.split(",")) for l in temp_f.readlines() )
        names = list(map(str, range(0, max(col_count))))

    return pd.read_csv(f, header=None, names=names)

def _batchFile(context: FileSystemContext, filename: str, idx: int, batch_size: Optional[int]):
    if batch_size is None:
        return context.resolve(f'{filename}.csv')

    batch_idx = int(idx // batch_size)
    return context.resolve(f'{filename}.{batch_idx}.csv')
