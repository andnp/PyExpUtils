from typing import Any, Optional, Sequence, Tuple

def flagString(pairs: Sequence[Tuple[str, Optional[Any]]], joiner: str = '='):
    s = ''
    for i, pair in enumerate(pairs):
        key, value = pair
        if value is not None:
            if i > 0: s += ' '
            s += f'{key}{joiner}{str(value)}'

    return s
