import sys
from typing import Any, Dict

class ArgsModel:
    def __init__(self, args: Dict[str, Any]):
        self.experiment_paths = list(args['experiment_paths'])
        self.runs = int(args['runs'])
        self.base_path = str(args['base_path'])
        self.executable = str(args['executable'])

        # optional
        self.retry = bool(args.get('retry', False))
        self.cpus = int(args.get('cpus', 1))

def fromCommandLine():
    if len(sys.argv) < 5:
        print('Please run again using')
        print('python -m scripts.scriptName [path/to/executable] [runs] [base_path] [paths/to/descriptions]...')
        exit(0)

    return ArgsModel({
        'experiment_paths': sys.argv[4:],
        'base_path': sys.argv[3],
        'runs': int(sys.argv[2]),
        'executable': sys.argv[1],
    })
