import re

def interpolate(s, d):
    keys = re.findall('{.*?}', s)

    final = s
    for key in keys:
        unwrapped = key[1:-1]
        value = d[unwrapped]
        final = final.replace(key, value)

    return final
