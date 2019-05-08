import tarfile

def inArchive(archive, path):
    exists = False
    # if there is no archive or the file isn't in the archive
    # then don't raise exception, just return false
    try:
        with tarfile.open(archive) as tar:
            tar.getmember(path)
            exists = True
    except:
        pass

    return exists

def getArchiveName(path):
    archive = path.split('/')[0]
    return archive + '.tar'
