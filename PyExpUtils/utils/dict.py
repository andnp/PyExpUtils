from PyExpUtils.utils.types import T
import re
from typing import Any, Dict, List, Sequence, overload

# making a type alias here just for readability
# using NewType('DictPath', str) is a huge pita for all consumers
DictPath = str

def merge(d1: Dict[Any, T], d2: Dict[Any, T]) -> Dict[Any, T]:
    ret = d2.copy()
    for key in d1:
        ret[key] = d2.get(key, d1[key])

    return ret

def flatKeys(d: Dict[Any, Any]) -> List[DictPath]:
    keys = d.keys()
    out: List[DictPath] = []
    for key in keys:
        if type(d[key]) is dict:
            sub_keys = flatKeys(d[key])
            out += [f'{key}.{subkey}' for subkey in sub_keys]

        elif type(d[key]) is list:
            sub_keys = []
            for i in range(len(d[key])):
                sub_keys.append(f'[{i}]')

            if type(d[key][0]) is dict:
                sub_keys = []
                for i, sub in enumerate(d[key]):
                    sub_keys += [ f'[{i}].{subkey}' for subkey in flatKeys(sub) ]

            out += [f'{key}.{subkey}' for subkey in sub_keys]

        else:
            out.append(key)

    return out


def hyphenatedStringify(d: Dict[Any, Any]):
    sorted_keys = sorted(flatKeys(d))
    parts = [f'{key}-{get(d, key)}' for key in sorted_keys]

    return '_'.join(parts)

@overload
def pick(d: Dict[Any, T], keys: DictPath) -> T:
    ...
@overload
def pick(d: Dict[Any, T], keys: List[DictPath]) -> Dict[Any, T]:
    ...
def pick(d, keys):
    if not isinstance(keys, list):
        return d[keys]

    r = {}
    for key in keys:
        r[key] = d[key]

    return r

def get(d: Any, key: DictPath, default: Any = None) -> Any:
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
