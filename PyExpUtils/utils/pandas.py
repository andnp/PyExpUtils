import pandas as pd
from functools import reduce
from typing import Iterable, Sequence

def inner(dfs: Iterable[pd.DataFrame], on: str | Sequence[str]):
    return reduce(lambda l, r: pd.merge(l, r, how='inner', on=on), dfs)

def outer(dfs: Iterable[pd.DataFrame], on: str | Sequence[str]):
    return reduce(lambda l, r: pd.merge(l, r, how='outer', on=on), dfs)
