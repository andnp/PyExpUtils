import os
from typing import Optional
from PyExpUtils.utils.archive import getArchiveName, inArchive
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

def listResultsPaths(exp: ExperimentDescription, runs: int = 1, key: Optional[str] = None):
    perms = exp.numPermutations()
    tasks = perms * runs
    for i in range(tasks):
        yield exp.interpolateSavePath(i, key=key)

def listMissingResults(exp: ExperimentDescription, runs: int = 1, key: Optional[str] = None):
    for path in listResultsPaths(exp, runs, key):
        archive = getArchiveName(path)
        if not os.path.exists(path) and not inArchive(archive, path):
            yield path
