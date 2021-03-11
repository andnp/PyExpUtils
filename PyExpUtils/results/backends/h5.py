import h5py
from typing import Any
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.utils.csv import buildCsvParams
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class Result(BaseResult):
    pass

def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './'):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    if '.' not in filename[-4:]:
        filename += '.h5'

    h5_file = save_context.resolve(filename)
    header = buildCsvParams(exp, idx)
    run = exp.getRun(idx)

    # h5py includes its own file-locking, no special handling need here
    with h5py.File(h5_file, 'a') as f:
        grp = f.create_group(header)
        grp.create_dataset(run, data=data)
