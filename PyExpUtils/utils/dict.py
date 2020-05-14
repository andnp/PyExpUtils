from PyExpUtils.utils.types import T
import re
from typing import Any, Dict, List, Sequence, Union, overload

def merge(d1: Dict[Any, T], d2: Dict[Any, T]) -> Dict[Any, T]:
    ret = d2.copy()
    for key in d1:
        ret[key] = d2.get(key, d1[key])

    return ret

def hyphenatedStringify(d: Dict[Any, Any]):
    sorted_keys = sorted(d.keys())
    parts = [str(key) + '-' + str(d[key]) for key in sorted_keys]
    return '_'.join(parts)

@overload
def pick(d: Dict[Any, T], keys: str) -> T:
    ...
@overload
def pick(d: Dict[Any, T], keys: List[Any]) -> Dict[Any, T]:
    ...
def pick(d, keys):
    if not isinstance(keys, list):
        return d[keys]

    r = {}
    for key in keys:
        r[key] = d[key]

    return r

def get(d: Any, key: str, default: Any = None) -> Any:
    if key == '':
        return d

    parts = key.split('.')

    el = d.get(parts[0])
    if el is None:
        return default

    if isinstance(el, list):
        idx = re.findall(r'\[(\d+)\]', parts[1])[0]
        idx = int(idx)
        if len(el) <= idx:
            return default

        return get(el[idx], '.'.join(parts[2:]), default)

    if isinstance(el, dict):
        return get(el, '.'.join(parts[1:]), default)

    return el

def equal(d1: Dict[T, Any], d2: Dict[T, Any], ignore: Sequence[T] = []):
    for k in d1:
        if k in ignore:
            continue

        if k not in d2:
            return False

        if d1[k] != d2[k]:
            return False

    return True
