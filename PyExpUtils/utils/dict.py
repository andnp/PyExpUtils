def merge(d1, d2):
    ret = d2.copy()
    for key in d1:
        ret[key] = d2.get(key, d1[key])

    return ret

def hyphenatedStringify(d):
    sorted_keys = sorted(d.keys())
    parts = [str(key) + '-' + str(d[key]) for key in sorted_keys]
    return '_'.join(parts)

def pick(d, keys):
    if not isinstance(keys, list):
        return d[keys]

    r = {}
    for key in keys:
        r[key] = d[key]

    return r

def equal(d1, d2, ignore=[]):
    for k in d1:
        if k in ignore:
            continue

        if k not in d2:
            return False

        if d1[k] != d2[k]:
            return False

    return True
