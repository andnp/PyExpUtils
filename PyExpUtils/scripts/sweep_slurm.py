import subprocess
from PyExpUtils.runner import SlurmArgs, parallel
from PyExpUtils.models import ExperimentDescription
from PyExpUtils.results.indices import listMissingResults, listIndices
from PyExpUtils.utils.generator import group
from PyExpUtils.runner.Slurm import schedule, slurmOptionsFromFile

args = SlurmArgs.fromCommandLine()
for path in args.experiment_paths:
    exp = ExperimentDescription.fromFile(path)
    slurm = slurmOptionsFromFile(args.slurm_path)

    # get all of the indices corresponding to missing results
    indices = listIndices(exp, args.runs) if args.retry else listMissingResults(exp, args.runs)

    groupSize = slurm.tasks * slurm.tasksPerNode

    for g in group(indices, groupSize):
        schedule(slurm, args.executable, g)
