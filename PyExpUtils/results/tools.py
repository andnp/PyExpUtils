import numpy as np
import pandas as pd

from typing import Any, Dict, Optional, Sequence

from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.utils.dict import flatKeys, get


def collapseRuns(df: pd.DataFrame):
    cols = list(df.columns)
    header = list(filter(lambda c: c not in ['data', 'run'], cols))

    df = df.groupby(header)['data'].apply(lambda x: np.array(list(x))).reset_index()
    return df

def subsetDF(df: pd.DataFrame, conds: Dict[str, Any]):
    mask = _buildMask(df, conds)
    return df[mask].reset_index(drop=True)

def splitByValue(df: pd.DataFrame, col: str):
    values = df[col].unique()
    values.sort()

    for v in values:
        sub = df[df[col] == v]
        yield v, sub

def getHeader(exp: ExperimentDescription):
    params = exp.getPermutation(0)['metaParameters']
    keys = flatKeys(params)
    return sorted(keys)

def getParamValues(exp: ExperimentDescription, idx: int, header: Optional[Sequence[str]] = None):
    if header is None:
        header = getHeader(exp)

    params = exp.getPermutation(idx)['metaParameters']
    return [get(params, k) for k in header]

def getParamsAsDict(exp: ExperimentDescription, idx: int, header: Optional[Sequence[str]] = None):
    if header is None:
        header = getHeader(exp)

    params = exp.getPermutation(idx)['metaParameters']
    return {
        k: get(params, k) for k in header
    }

# ------------------------
# -- Internal Utilities --
# ------------------------
def _buildMask(df: pd.DataFrame, conds: Dict[str, Any]):
    mask = np.ones(len(df), dtype=bool)
    for key, cond in conds.items():
        if isinstance(cond, dict):
            mask = mask | _buildMask(df, cond)

        elif isinstance(cond, list):
            mask = mask & (df[key].isin(cond))

        elif key in df:
            mask = mask & (df[key] == cond)

    return mask
