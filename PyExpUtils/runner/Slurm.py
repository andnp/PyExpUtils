import os
import json
from typing import Any, Dict, Iterator, Optional, Sequence, Tuple
import PyExpUtils.runner.parallel as Parallel
from PyExpUtils.utils.types import optionalCast
from PyExpUtils.results.indices import listMissingResults, listIndices

"""doc
Takes an integer number of hours and returns a well-formated time string.
```python
time = hours(3)
print(time) # -> '2:59:59
```
"""
def hours(n: int):
    return f'{n-1}:59:59'

"""doc
Takes an integer number of gigabytes and returns a well-formated memory string.
```python
memory = gigs(4)
print(memory) # -> '4G'
```
"""
def gigs(n: int):
    return f'{n}G'

def flagString(pairs: Sequence[Tuple[str, Optional[Any]]]):
    s = ''
    for i, pair in enumerate(pairs):
        key, value = pair
        if value is not None:
            if i > 0: s += ' '
            s += f'{key}={str(value)}'

    return s

class Options:
    def __init__(self, d: Dict[str, Any]):
        self.account = str(d['account'])
        self.time = str(d['time'])
        self.cores = optionalCast(int, d.get('cores'))
        self.nodes = optionalCast(int, d.get('nodes'))
        self.memPerCpu = optionalCast(str, d.get('memPerCpu'))
        self.tasksPerNode = optionalCast(int, d.get('tasksPerNode'))
        self.sequential = optionalCast(int, d.get('sequential'))

        self.output = optionalCast(str, d.get('output', '$SCRATCH/job_output_%j.txt'))
        self.emailType = d.get('emailType')
        self.email = d.get('email')

        # TODO: do some sanity checking of arguments here
        # if Nodes are specified, then mem-per-cpu should not be nor should nodes be

    def cmdArgs(self):
        args = [
            ('--account', self.account),
            ('--time', self.time),
            ('--ntasks', self.cores),
            ('--nodes', self.nodes),
            ('--ntasks-per-node', self.tasksPerNode),
            ('--mem-per-cpu', self.memPerCpu),
            ('--output', self.output),
            ('--mail-type', self.emailType),
            ('--mail-user', self.email),
        ]
        return flagString(args)

def fromFile(path: str):
    with open(path, 'r') as f:
        d = json.load(f)

    return Options(d)

def buildParallel(executable: str, tasks: Iterator[Any], opts: Dict[str, Any] = {}):
    nodes = opts.get('nodes-per-process', 1)
    threads = opts.get('threads-per-process', 1)
    return Parallel.build({
        'executable': f'srun -N{nodes} -n{threads} --exclusive {executable}',
        'tasks': tasks,
        'cores': opts['ntasks']
    })

def schedule(script: str, opts: Optional[Options] = None, script_name: str = 'auto_slurm.sh', cleanup: bool = True):
    with open(script_name, 'w') as f:
        f.write(script)

    cmdArgs = ''
    if opts is not None:
        cmdArgs = opts.cmdArgs()

    os.system(f'sbatch {cmdArgs} {script_name}')

    if cleanup:
        os.remove(script_name)
