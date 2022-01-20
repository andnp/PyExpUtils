import re
from PyExpUtils.utils.dict import DictPath, flatKeys, get
from PyExpUtils.utils.arrays import deduplicate, last
from typing import Dict, Any, List, Tuple

Record = Dict[str, Any]
PathDict = Dict[DictPath, Any]
KVPair = Tuple[DictPath, List[Any]]

# -----------------------------------------------------------------------------
# clean public api

def getParameterPermutation(sweeps: Record, index: int):
    pairs = _flattenToKeyValues(sweeps)
    return getPermutationFromPairs(pairs, index)


def getNumberOfPermutations(sweeps: Record):
    pairs = _flattenToKeyValues(sweeps)
    return getCountFromPairs(pairs)

# -----------------------------------------------------------------------------

def getPermutationFromPairs(pairs: List[KVPair], index: int):
    perm: PathDict = {}
    accum = 1

    for key, values in pairs:
        num = len(values)

        # if we have an empty array for a parameter, add that parameter back as an empty array
        if num == 0:
            perm[key] = []
            continue

        perm[key] = values[(index // accum) % num]
        accum *= num

    return reconstructParameters(perm)

def getCountFromPairs(pairs: List[KVPair]):
    accum = 1
    for pair in pairs:
        _, values = pair
        num = len(values) if len(values) > 0 else 1
        accum *= num

    return accum

def dropLastArray(key: str):
    parts = key.split('.')

    # if the last part of the dict path is an element in an array
    # then just drop that part
    if re.match(r'\[\d+\]', last(parts)):
        return '.'.join(parts[:-1])

    return '.'.join(parts)

def reconstructParameters(perm: PathDict):
    res: Record = {}
    for key in perm:
        set_at_path(res, key, perm[key])

    return res

def _flattenToKeyValues(sweeps: Record):
    keys = flatKeys(sweeps)
    keys = list(map(dropLastArray, keys))
    keys = deduplicate(keys)
    keys = sorted(keys)

    out: List[Tuple[DictPath, List[Any]]] = []
    for key in keys:
        values = get(sweeps, key)

        # allow parameters to be set like "alpha": 0.1 as a shortcut
        if type(values) is not list:
            values = [values]

        out.append((key, values))

    return out

# TODO: move this to the utils.dict folder and try to compress/simplify it
# then add unit tests
def set_at_path(d: Record, path: DictPath, val: Any):
    def inner(d: Record, path: DictPath, val: Any, last: str) -> Record:
        if len(path) == 0: return d
        split = path.split('.', maxsplit=1)

        part, rest = split if len(split) > 1 else [split[0], '']
        nxt = rest.split('.')[0]

        # lists
        if part.startswith('['):
            num = int(re.sub(r'[\[,\]]', '', part))

            if len(d[last]) > num:
                piece = inner(d[last][num], rest, val, '') if len(rest) > 0 else val
                d[last][num] = piece
            else:
                piece = inner({}, rest, val, '') if len(rest) > 0 else val
                d[last].append(piece)
            return d

        # objects
        elif len(rest) > 0:
            if nxt.startswith('['):
                piece = d.setdefault(part, [])
                return inner(d, rest, val, part)
            else:
                piece = d.setdefault(part, {})
                return inner(piece, rest, val, part)

        # everything else
        else:
            d.setdefault(part, val)
            return d

    inner(d, path, val, '')
    return d
