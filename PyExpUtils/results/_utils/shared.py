from typing import Any, Iterable

def hash_values(vals: Iterable[Any]):
    return hash(','.join(map(str, vals)))
