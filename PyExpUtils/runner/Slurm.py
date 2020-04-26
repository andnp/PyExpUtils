import os
import json
from typing import Any, Dict, Iterator, Optional
import PyExpUtils.runner.parallel as Parallel
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

class Options:
    def __init__(self, d: Dict[str, Any]):
        self.account = str(d['account'])
        self.time = str(d['time'])
        self.tasks = int(d['nodes'])
        self.memPerCpu = str(d['memPerCpu'])
        self.tasksPerNode = int(d['tasksPerNode'])

        self.output = str(d.get('output', '$SCRATCH/job_output_%j.txt'))
        self.emailType = d.get('emailType')
        self.email = d.get('email')

    def cmdArgs(self):
        args = [
            f'--account={self.account}',
            f'--time={self.time}',
            f'--ntasks={self.tasks}',
            f'--mem-per-cpu={self.memPerCpu}',
            f'--output={self.output}',
        ]
        if self.emailType is not None: args.append(f'--mail-type={self.emailType}')
        if self.email is not None: args.append(f'--main-user={self.email}')
        return ' '.join(args)

def fromFile(path: str):
    with open(path, 'r') as f:
        d = json.load(f)

    return Options(d)

def buildParallel(executable: str, tasks: Iterator[Any], opts: Dict[str, Any] = {}):
    nodes = opts.get('nodes-per-process', 1)
    threads = opts.get('threads-per-process', 1)
    return Parallel.build({
        'executable': f'srun -N{nodes} -n{threads} {executable}',
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
