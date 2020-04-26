import re

from typing import Dict, Any, List, NewType, Tuple, cast
Record = Dict[str, Any]

ObjectPath = NewType('ObjectPath', str)
PathDict = Dict[ObjectPath, Any]

def getParameterPermutation(sweeps: Record, index: int):
    pairs = flattenToArray(sweeps)
    perm: PathDict = {}
    accum = 1

    for pair in pairs:
        key, values = pair
        num = len(values)

        # if we have an empty array for a parameter, add that parameter back as an empty array
        if num == 0:
            perm[key] = []
            continue

        perm[key] = values[(index // accum) % num]
        accum *= num

    return reconstructParameters(perm)

def getNumberOfPermutations(thing: Record):
    pairs = flattenToArray(thing)
    accum = 1
    for pair in pairs:
        _, values = pair
        num = len(values) if len(values) > 0 else 1
        accum *= num

    return accum

# -----------------------------------------------------------------------------

def reconstructParameters(perm: PathDict):
    res: Record = {}
    for key in perm:
        set_at_path(res, key, perm[key])

    return res

def flattenToArray(thing: Record):
    accum: List[Tuple[ObjectPath, Any]] = []

    def inner(it: Any, path: ObjectPath):
        if isinstance(it, list):
            # check if list contains objects
            # if it does, keep recurring
            if isinstance(it[0], dict):
                i = 0
                for sub in it:
                    new_path = cast(ObjectPath, f'{path}.[{i}]')
                    inner(sub, new_path)
                    i += 1

                return

            accum.append((path, it))
            return

        if isinstance(it, dict):
            for key in sorted(it):
                new_path = key if path == '' else f'{path}.{key}'
                new_path = cast(ObjectPath, new_path)
                inner(it[key], new_path)

            return

        accum.append(( path, [it] ))
        return

    inner(thing, cast(ObjectPath, ''))
    return accum

def set_at_path(d: Record, path: str, val: Any):
    def inner(d: Record, path: str, val: Any, last: str):
        if len(path) == 0: return d
        split = path.split('.', maxsplit = 1)

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
