import numpy as np
import numpy.typing as npt
from PyExpUtils.utils.arrays import unwrap
from typing import Any, Callable, Iterable, List, Optional
from PyExpUtils.utils.dict import flatKeys, get, pick
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

def buildCsvParams(exp: ExperimentDescription, idx: int):
    params = pick(exp.getPermutation(idx), unwrap(exp.getKeys()))
    keys = flatKeys(params)
    keys = sorted(keys)

    values: List[str] = []
    for key in keys:
        values.append(str(get(params, key)))

    return ','.join(values)

def buildCsvHeader(exp: ExperimentDescription):
    params = pick(exp.getPermutation(0), unwrap(exp.getKeys()))
    keys = flatKeys(params)
    keys = sorted(keys)

    return ','.join(keys)

def buildPrecisionStr(p: float):
    return ('{:.' + str(p) + 'f}').format

def arrayToCsv(data: npt.ArrayLike, precision: Optional[int] = None):
    if precision is None:
        toStr: Callable[[Any], str] = str
    elif precision == 0:
        toStr = lambda x: str(int(x))
    else:
        toStr = buildPrecisionStr(precision)

    if np.ndim(data) == 0:
        return toStr(data)

    assert isinstance(data, Iterable)
    return ','.join(map(toStr, data))
