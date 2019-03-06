import sys
from PyExpUtils.runner.Args import ArgsModel

class SlurmArgsModel(ArgsModel):
    def __init__(self, d):
        super().__init__(d)

        self.slurm_path = d['slurm_path']

def fromCommandLine():
    if len(sys.argv) < 6:
        print('Please run again using')
        print('python -m scripts.scriptName [path/to/executable] [path/to/slurm-def] [runs] [base_path] [paths/to/descriptions]...')
        exit(0)

    return SlurmArgsModel({
        'experiment_paths': sys.argv[5:],
        'base_path': sys.argv[4],
        'runs': int(sys.argv[3]),
        'slurm_path': sys.argv[2],
        'executable': sys.argv[1],
    })
