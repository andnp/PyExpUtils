import subprocess
from PyExpUtils.runner import SlurmArgs, parallel
from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.indices import listMissingResults, listIndices
from PyExpUtils.utils.generator import group
from PyExpUtils.runner.Slurm import schedule, slurmOptionsFromFile

def call(args = None, model=ExperimentDescription, buildExecutable = None):
    if args is None:
        args = SlurmArgs.fromCommandLine()

    for path in args.experiment_paths:
        exp = loadExperiment(path, Model=model)
        slurm = slurmOptionsFromFile(args.slurm_path)

        # get all of the indices corresponding to missing results
        indices = listIndices(exp, args.runs) if args.retry else listMissingResults(exp, args.runs)

        executable = args.executable
        if buildExecutable is not None:
            executable = buildExecutable(exp)

    groupSize = slurm.tasks * slurm.tasksPerNode

    for g in group(indices, groupSize):
        schedule(slurm, executable, g)
