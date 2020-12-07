from PyExpUtils.utils.arrays import unwrap
from typing import Any, Callable, Optional
from PyExpUtils.utils.dict import flatKeys, get, pick
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

def buildCsvParams(exp: ExperimentDescription, idx: int):
    params = pick(exp.getPermutation(idx), unwrap(exp._getKeys()))
    keys = flatKeys(params)
    keys = sorted(keys)

    values = []
    for key in keys:
        values.append(str(get(params, key)))

    return ','.join(values)

def buildCsvHeader(exp: ExperimentDescription):
    params = pick(exp.getPermutation(0), unwrap(exp._getKeys()))
    keys = flatKeys(params)
    keys = sorted(keys)

    return ','.join(keys)

def buildPrecisionStr(p: int):
    return lambda x: ('{:.' + str(p) + 'f}').format(x)

def arrayToCsv(data, precision: Optional[int] = None):
    if precision is None:
        toStr: Callable[[Any], str] = str
    elif precision == 0:
        toStr = lambda x: str(int(x))
    else:
        toStr = buildPrecisionStr(precision)

    return ','.join(map(toStr, data))
