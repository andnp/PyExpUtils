import shlex
import subprocess
import signal

from dataclasses import dataclass
from typing import Dict, Sequence
from multiprocessing.dummy import Pool
from functools import partial

from PyExpUtils.utils.generator import group

@dataclass
class ParallelConfig:
    executable: str
    parallel: int
    tasks: Sequence[int]
    sequential: int = 1


def execute(c: ParallelConfig):
    task_seq = group(c.tasks, c.sequential)
    task_strs = map(_stringify_group, task_seq)
    execs = map(lambda t: f'{c.executable} {t}', task_strs)

    procs: Dict[int, subprocess.Popen] = {}

    def _handler(sig, frame):
        for p in procs.values():
            p.send_signal(signal.SIGUSR1)

    signal.signal(signal.SIGUSR1, _handler)

    with Pool(c.parallel) as p:
        p.map(partial(_exec, procs=procs), execs)

def _exec(cmd: str, procs):
    parts = shlex.split(cmd)
    process = subprocess.Popen(parts)
    procs[process.pid] = process
    process.wait()
    del procs[process.pid]

def _stringify_group(g: Sequence[int]) -> str:
    return ', '.join(map(str, g))
