import subprocess
from PyExpUtils.runner import Args, parallel
from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.indices import listMissingResults, listIndices

def call(args = None, model=ExperimentDescription, buildExecutable = None):
    if args is None:
        args = Args.fromCommandLine()

    for path in args.experiment_paths:
        exp = loadExperiment(path, Model=model)

        # get all of the indices corresponding to missing results
        indices = listIndices(exp, args.runs) if args.retry else listMissingResults(exp, args.runs)

        executable = args.executable
        if buildExecutable is not None:
            executable = buildExecutable(exp)

        # build the parallel command
        maybe_parallel_cmd = parallel.buildParallel({
            'executable': executable,
            'tasks': indices,
            'cores': args.cpus,
        })

        maybe_parallel_cmd.map(lambda cmd: subprocess.run(cmd, stdout=subprocess.PIPE, shell=True))
