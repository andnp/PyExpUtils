from typing import Any, Optional, Iterable, Tuple

def flagString(pairs: Iterable[Tuple[str, Optional[Any]]], joiner: str = '='):
    pairs = filter(lambda p: p[1] is not None, pairs)
    pairs = sorted(pairs)

    s = ''
    for i, pair in enumerate(pairs):
        key, value = pair
        if i > 0: s += ' '
        s += f'{key}{joiner}{str(value)}'

    return s
