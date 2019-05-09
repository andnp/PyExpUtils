import tarfile
from PyExpUtils.utils.fp import memoize

@memoize
def openTar(archive):
    return tarfile.open(archive)

def inArchive(archive, path):
    exists = False
    # if there is no archive or the file isn't in the archive
    # then don't raise exception, just return false
    try:
        tar = openTar(archive)
        tar.getmember(path)
        exists = True
    except:
        pass

    return exists

def getArchiveName(path):
    archive = path.split('/')[0]
    return archive + '.tar'
