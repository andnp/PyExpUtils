import os
import time
import shutil
import PyExpUtils.utils.path as Path

class FileSystemContext:
    def __init__(self, path, base = ''):
        self._path = path
        self._base = base

    def getBase(self):
        return self._base

    def resolve(self, path = ''):
        base = Path.join(self.getBase(), self._path)

        path = path.replace(base + '/', '')

        while path.startswith('../'):
            path = path[3:]
            base = base.split('/')[:-1]
            base = '/'.join(base)

        if path == '':
            return base

        return Path.join(base, path)

    def ensureExists(self, path = ''):
        path = self.resolve(path)
        os.makedirs(path, exist_ok=True)

    def remove(self, path = ''):
        files = self.resolve(path)
        shutil.rmtree(files)
