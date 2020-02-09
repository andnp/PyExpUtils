import os
import json
import PyExpUtils.runner.parallel as Parallel
from PyExpUtils.results.indices import listMissingResults, listIndices

"""doc
Takes an integer number of hours and returns a well-formated time string.
```python
time = hours(3)
print(time) # -> '2:59:59
```
"""
def hours(n):
    return f'{n-1}:59:59'

"""doc
Takes an integer number of gigabytes and returns a well-formated memory string.
```python
memory = gigs(4)
print(memory) # -> '4G'
```
"""
def gigs(n):
    return f'{n}G'

class Options:
    def __init__(self, d):
        self.account = d['account']
        self.time = d['time']
        self.tasks = d['nodes']
        self.memPerCpu = d['memPerCpu']
        self.tasksPerNode = d['tasksPerNode']

        self.output = d.get('output', '$SCRATCH/job_output_%j.txt')
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

def fromFile(path):
    with open(path, 'r') as f:
        d = json.load(f)

    return Options(d)

def buildParallel(executable, tasks, opts={}):
    nodes = opts.get('nodes-per-process', 1)
    threads = opts.get('threads-per-process', 1)
    return Parallel.buildParallel({
        'executable': f'srun -N{nodes} -n{threads} {executable}',
        'tasks': tasks,
        'cores': opts['ntasks']
    })

def schedule(script, opts=None, script_name='auto_slurm.sh', cleanup=True):
    with open(script_name, 'w') as f:
        f.write(script)

    cmdArgs = ''
    if opts is None:
        cmdArgs = opts.cmdArgs()

    os.system(f'sbatch {cmdArgs} {script_name}')

    if cleanup:
        os.remove(script_name)
