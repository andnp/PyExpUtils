import os
import re
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import PyExpUtils.runner.parallel as Parallel
from PyExpUtils.utils.cmdline import flagString

"""doc
Takes an integer number of hours and returns a well-formatted time string.
```python
time = hours(3)
print(time) # -> '2:59:59
```
"""
def hours(n: int):
    return f'{n-1}:59:59'

"""doc
Takes an integer number of gigabytes and returns a well-formatted memory string.
```python
memory = gb(4)
print(memory) # -> '4G'
```
"""
def gb(n: int):
    return f'{n}G'


@dataclass
class SingleNodeOptions:
    account: str
    time: str
    cores: int
    mem_per_core: str | float

    # task management args
    sequential: int = 1
    threads_per_task: int = 1

    # job reporting args
    log_path: str = "$SCRATCH/job_output_%j.txt"

@dataclass
class MultiNodeOptions:
    account: str
    time: str
    cores: int
    mem_per_core: str | float

    # task management args
    sequential: int = 1

    # job reporting args
    log_path: str = "$SCRATCH/job_output_%j.txt"

# ----------------
# -- Validation --
# ----------------
def check_account(account: str):
    assert account.startswith('rrg-') or account.startswith('def-')
    assert not account.endswith('_cpu') and not account.endswith('_gpu')

def check_time(time: str):
    assert isinstance(time, str)

    # while technically slurm is more permissive, I find being more explicit removes
    # some common footguns. Example the "int:int" format is oft misunderstood as "hours:minutes"

    # "hour:minute:second"
    h_m_s = re.match(r'^\d+:\d+:\d+$', time)

    # "days-hours"
    d_h = re.match(r'^\d+-\d+$', time)

    # "days-hours:minutes:seconds"
    d_h_m_s = re.match(r'^\d+-\d+:\d+:\d+$', time)

    assert h_m_s or d_h or d_h_m_s

def normalize_memory(memory: float | str) -> str:
    if isinstance(memory, (float, int)):
        mbs = int(memory * 1024)
        memory = f'{mbs}M'

    assert isinstance(memory, str)
    assert re.match(r'^\d+[G|M|K]$', memory)
    return memory

def shared_validation(options: SingleNodeOptions | MultiNodeOptions):
    check_account(options.account)
    check_time(options.time)
    options.mem_per_core = normalize_memory(options.mem_per_core)


def single_validation(options: SingleNodeOptions):
    shared_validation(options)
    # TODO: validate that the current cluster has nodes that can handle the specified request

def multi_validation(options: MultiNodeOptions):
    shared_validation(options)

def validate(options: SingleNodeOptions | MultiNodeOptions):
    if isinstance(options, SingleNodeOptions): single_validation(options)
    elif isinstance(options, MultiNodeOptions): multi_validation(options)

# ------------------
# -- External API --
# ------------------

def memory_in_mb(memory: str | float) -> float:
    memory = normalize_memory(memory)

    if memory.endswith('M'):
        return int(memory[:-1])

    if memory.endswith('G'):
        return int(memory[:-1]) * 1024

    if memory.endswith('K'):
        return int(memory[:-1]) / 1024

    raise Exception('Unknown memory unit')

def to_cmdline_flags(options: SingleNodeOptions | MultiNodeOptions):
    validate(options)
    args = [
        ('--account', options.account),
        ('--time', options.time),
        ('--mem-per-cpu', options.mem_per_core),
        ('--output', options.log_path),
    ]

    if isinstance(options, SingleNodeOptions):
        args += [
            ('--ntasks', 1),
            ('--nodes', 1),
            ('--ntasks-per-node', options.cores),
        ]

    elif isinstance(options, MultiNodeOptions):
        args += [
            ('--ntasks', options.cores),
            ('--cpus-per-task', 1),
        ]

    return flagString(args)

def fromFile(path: str):
    with open(path, 'r') as f:
        d = json.load(f)

    assert 'type' in d, 'Need to specify scheduling strategy.'
    t = d['type']
    del d['type']

    if t == 'single_node':
        return SingleNodeOptions(**d)

    elif t == 'multi_node':
        return MultiNodeOptions(**d)

    raise Exception('Unknown scheduling strategy')

def buildParallel(executable: str, tasks: Iterable[Any], opts: SingleNodeOptions | MultiNodeOptions, parallelOpts: Dict[str, Any] = {}):
    threads = 1
    if isinstance(opts, SingleNodeOptions):
        threads = opts.threads_per_task

    cores = int(opts.cores / threads)

    parallel_exec = f'srun -N1 -n{threads} --exclusive {executable}'
    if isinstance(opts, SingleNodeOptions):
        parallel_exec = executable

    return Parallel.build({
        'executable': parallel_exec,
        'tasks': tasks,
        'cores': cores,
        'delay': 0.5, # because srun interacts with the scheduler, a slight delay helps prevent intermittent errors
    } | parallelOpts)

def schedule(script: str, opts: Optional[SingleNodeOptions | MultiNodeOptions] = None, script_name: str = 'auto_slurm.sh', cleanup: bool = True):
    with open(script_name, 'w') as f:
        f.write(script)

    cmdArgs = ''
    if opts is not None:
        cmdArgs = to_cmdline_flags(opts)

    os.system(f'sbatch {cmdArgs} {script_name}')

    if cleanup:
        os.remove(script_name)
