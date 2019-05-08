import os
from PyExpUtils.utils.path import rest
from PyExpUtils.utils.archive import getArchiveName, inArchive

def listResultsPaths(exp, runs=1):
    perms = exp.permutations()
    tasks = perms * runs
    for i in range(tasks):
        yield exp.interpolateSavePath(i)

def listMissingResults(exp, runs=1):
    for path in listResultsPaths(exp, runs):
        archive = getArchiveName(path)
        if not os.path.exists(path) and not inArchive(archive, rest(path)):
            yield path
