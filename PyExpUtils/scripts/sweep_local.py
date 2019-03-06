import subprocess
from PyExpUtils.runner import Args, parallel
from PyExpUtils.models import ExperimentDescription
from PyExpUtils.results.indices import listMissingResults, listIndices

args = Args.fromCommandLine()
for path in args.experiment_paths:
    exp = ExperimentDescription.fromFile(path)

    # get all of the indices corresponding to missing results
    indices = listIndices(exp, args.runs) if args.retry else listMissingResults(exp, args.runs)

    # build the parallel command
    parallel_cmd = parallel.buildParallel({
        'executable': args.executable,
        'tasks': indices,
        'cores': args.cpus,
    })

    subprocess.run(parallel, stdout=subprocess.PIPE, shell=True)
