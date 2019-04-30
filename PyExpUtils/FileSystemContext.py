import os
import time
import shutil
import tarfile

class FileSystemContext:
    def __init__(self, path, base = '', use_tmp = False):
        self._path = path
        self._base = base
        self._use_tmp = use_tmp

        pid = os.getpid()
        epoch = int(time.time() * 1000)

        self._tmp_dir = f'{pid}.{epoch}'

    def getBase(self):
        if self._use_tmp:
            return f'{self._base}/{self._tmp_dir}'

        return f'{self._base}'

    def resolve(self, path = ''):
        base = self.getBase() + '/' + self._path

        path = path.replace(base + '/', '')

        while path.startswith('../'):
            path = path[3:]
            base = base.split('/')[:-1]
            base = '/'.join(base)

        if path == '':
            return base

        return f'{base}/{path}'

    def ensureExists(self, path = ''):
        path = self.resolve(path)
        os.makedirs(path, exist_ok=True)

    def archive(self, fr = '', to = None):
        files = self.resolve(fr)
        archive = self._path.split('/')[0] + '.tar' if to is None else to

        with tarfile.open(archive, 'a') as tar:
            tar.add(files, files.replace(self._base + '/', ''), True)

        return archive

    def remove(self, path = ''):
        files = self.resolve(path)
        shutil.rmtree(files)
