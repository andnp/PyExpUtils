import tarfile
from PyExpUtils.utils.fp import memoize

@memoize
def openTar(archive: str):
    return tarfile.open(archive)

def inArchive(archive: str, path: str):
    exists = False
    # if there is no archive or the file isn't in the archive
    # then don't raise exception, just return false
    try:
        tar = openTar(archive)
        tar.getmember(path)
        exists = True
    except Exception:
        pass

    return exists

def getArchiveName(path: str):
    archive = path.split('/')[0]
    return archive + '.tar'
