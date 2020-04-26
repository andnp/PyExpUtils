import re
from typing import Dict, Any

def interpolate(s: str, d: Dict[str, Any]):
    keys = re.findall('{.*?}', s)

    final = s
    for key in keys:
        unwrapped = key[1:-1]
        value = str(d[unwrapped])
        final = final.replace(key, value)

    return final
