import sys

class ArgsModel:
    def __init__(self, args):
        self.experiment_paths = args['experiment_paths']
        self.runs = args['runs']
        self.base_path = args['base_path']
        self.executable = args['executable']

        # optional
        self.retry = args.get('retry', False)
        self.cpus = args.get('cpus', 1)

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
