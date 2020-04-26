import os
import shutil
import PyExpUtils.utils.path as Path

class FileSystemContext:
    def __init__(self, path: str, base: str = ''):
        self._path = path
        self._base = base

    def getBase(self):
        return self._base

    def resolve(self, path: str = ''):
        base = Path.join(self._base, self._path)

        path = path.replace(base + '/', '')

        while path.startswith('../'):
            path = path[3:]
            base = Path.up(base)

        if path == '':
            return base

        return Path.join(base, path)

    def ensureExists(self, path: str = ''):
        path = self.resolve(path)
        os.makedirs(path, exist_ok=True)

    def remove(self, path: str = ''):
        files = self.resolve(path)
        shutil.rmtree(files)
