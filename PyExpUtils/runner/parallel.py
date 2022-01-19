from typing import Any, Dict
from PyExpUtils.utils.cmdline import flagString

def build(d: Dict[str, Any]):
    # required
    ex = d['executable']
    cores = d['cores']
    tasks = d['tasks']

    # make sure tasks is a string
    tasks = tasks if isinstance(tasks, str) else ' '.join(map(str, tasks))

    # optional
    delay = d.get('delay')
    sshloginfile = d.get('sshloginfile')
    batch = d.get('batch')

    # build parameter pairs
    pairs = [
        ('-j', cores),
        ('--delay', delay),
        ('--sshloginfile', sshloginfile),
        ('-n', batch),
    ]

    # build parallel options
    ops = flagString(pairs, joiner=' ')

    if len(tasks) == 0:
        return None

    return f'parallel {ops} {ex} ::: {tasks}'
