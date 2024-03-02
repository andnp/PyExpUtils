#!/usr/bin/env python

import argparse
from PyExpUtils.runner.parallel_exec import ParallelConfig, execute

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', type=int, required=True)
    parser.add_argument('--exec', type=str, required=True)
    parser.add_argument('--seq', type=int, required=False, default=1)
    parser.add_argument('--tasks', nargs='+', type=int, required=True)

    args = parser.parse_args()

    config = ParallelConfig(
        executable=args.exec,
        parallel=args.parallel,
        sequential=args.seq,
        tasks=args.tasks,
    )

    execute(config)
