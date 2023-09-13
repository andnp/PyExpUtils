import pandas as pd
from functools import reduce
from typing import Any, Dict, Iterable, Sequence

def inner(dfs: Iterable[pd.DataFrame], on: str | Sequence[str]):
    return reduce(lambda l, r: pd.merge(l, r, how='inner', on=on), dfs)

def outer(dfs: Iterable[pd.DataFrame], on: str | Sequence[str]):
    return reduce(lambda l, r: pd.merge(l, r, how='outer', on=on), dfs)


def query(df: pd.DataFrame, d: Dict[str, Any]):
    if len(d) == 0:
        return df

    keys = d.keys()
    for k in keys:
        assert k in df, f"Can't query df. Unknown key {k} in {df.columns}"

    q = ' & '.join(f'`{k}`=={_maybe_quote(v)}' for k, v in d.items())
    return df.query(q)

def _maybe_quote(v: Any):
    if isinstance(v, str):
        return _quote(v)
    return v

def _quote(s: str):
    return f'"{s}"'
