import unittest
import os
import shutil
from PyExpUtils.FileSystemContext import FileSystemContext

class TestFileSystemContext(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree('.tmp')
            os.remove('path.tar')
        except:
            pass

    def test_getBase(self):
        ctx = FileSystemContext('path/to/results', 'scratch')

        got = ctx.getBase()
        expected = 'scratch'

        self.assertEqual(got, expected)

    def test_resolveEmpty(self):
        ctx = FileSystemContext('path/to/results', 'scratch')

        got = ctx.resolve()
        expected = 'scratch/path/to/results'

        self.assertEqual(got, expected)

    def test_resolveFile(self):
        ctx = FileSystemContext('path/to/results', 'scratch')

        got = ctx.resolve('rmsve.npy')
        expected = 'scratch/path/to/results/rmsve.npy'

        self.assertEqual(got, expected)

    def test_resolveFull(self):
        ctx = FileSystemContext('path/to/results', 'scratch')

        got = ctx.resolve('scratch/path/to/results/rmsve.npy')
        expected = 'scratch/path/to/results/rmsve.npy'

        self.assertEqual(got, expected)

    def test_resolveParentDir(self):
        ctx = FileSystemContext('path/to/results', 'scratch')

        got = ctx.resolve('../experiment.json')
        expected = 'scratch/path/to/experiment.json'

        self.assertEqual(got, expected)

    def test_remove(self):
        ctx = FileSystemContext('path/to/results', '.tmp/test_remove')

        ctx.ensureExists()
        path = ctx.resolve('test.txt')
        with open(path, 'w') as f:
            f.write('hey there')

        self.assertTrue(os.path.isfile(f'{ctx.getBase()}/path/to/results/test.txt'))

        ctx.remove()
        self.assertFalse(os.path.isfile(f'{ctx.getBase()}/path/to/results/test.txt'))

class TestRegressions(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree('.tmp')
            os.remove('path.tar')
        except:
            pass

    def test_resolveNoBase(self):
        ctx = FileSystemContext('path/to/results')

        got = ctx.resolve('test.txt')
        expected = 'path/to/results/test.txt'

        self.assertEqual(got, expected)