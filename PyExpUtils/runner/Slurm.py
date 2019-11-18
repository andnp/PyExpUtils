import os
import json
from PyExpUtils.runner.parallel import buildParallel
from PyExpUtils.results.indices import listMissingResults, listIndices

def hours(n):
    return f'{n-1}:59:00'

def gigs(n):
    return f'{n}G'

class SlurmOptions:
    def __init__(self, d):
        self.account = d['account']
        self.time = d['time']
        self.tasks = d['nodes']
        self.memPerCpu = d['memPerCpu']
        self.tasksPerNode = d['tasksPerNode']

        self.output = d.get('output', '$SCRATCH/job_output_\%j.txt')
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

def slurmOptionsFromFile(path):
    with open(path, 'r') as f:
        d = json.load(f)

    return SlurmOptions(d)

def _slurmFile(slurm, parallel, preamble, postamble):
    cwd = os.getcwd()
    return f'''#!/bin/bash
{preamble}
cd {cwd}
{parallel}
{postamble}
    '''

def schedule(slurm, executable, tasks, preamble='', postamble='', debug=False):
    maybe_parallel = buildParallel({
        'executable': f'srun -N1 -n1 {executable}',
        'tasks': tasks,
        'cores': slurm.tasks,
    })

    if maybe_parallel.empty():
        return

    parallel = maybe_parallel.insist()

    slurm_str = _slurmFile(slurm, parallel, preamble, postamble)

    if debug:
        print("Would schedule this bash script:")
        print(slurm_str)
        return

    with open('auto_slurm.sh', 'w') as f:
        f.write(slurm_str)

    os.system(f'sbatch {slurm.cmdArgs()} auto_slurm.sh')
    os.remove('auto_slurm.sh')
