import os
from PyExpUtils.utils.path import rest
from PyExpUtils.utils.archive import getArchiveName, inArchive

def listResultsPaths(exp, runs=1, key=None):
    perms = exp.numPermutations()
    tasks = perms * runs
    for i in range(tasks):
        yield exp.interpolateSavePath(i, key=key)

def listMissingResults(exp, runs=1, key=None):
    for path in listResultsPaths(exp, runs, key):
        archive = getArchiveName(path)
        if not os.path.exists(path) and not inArchive(archive, path):
            yield path
