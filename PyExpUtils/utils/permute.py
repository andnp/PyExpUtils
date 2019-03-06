import re

def getParameterPermutation(sweeps, index):
    pairs = flattenToArray(sweeps)
    perm = {}
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

def reconstructParameters(perm):
    res = {}
    for key in perm:
        set_at_path(res, key, perm[key])

    return res


def getNumberOfPermutations(thing):
    pairs = flattenToArray(thing)
    accum = 1
    for pair in pairs:
        path, values = pair
        num = len(values) if len(values) > 0 else 1
        accum *= num

    return accum

def flattenToArray(thing):
    accum = []

    def inner(thing, path):
        if isinstance(thing, list):
            # check if list contains objects
            # if it does, keep recurring
            if isinstance(thing[0], dict):
                i = 0
                for sub in thing:
                    inner(sub, f'{path}.[{i}]')
                    i += 1
                return

            accum.append((path, thing))
            return

        if isinstance(thing, dict):
            for key in thing:
                new_path = key if path == '' else f'{path}.{key}'
                inner(thing[key], new_path)
            return

        accum.append(( path, [thing] ))
        return

    inner(thing, '')
    return accum

def set_at_path(d, path, val):
    def inner(d, path, val, last):
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
