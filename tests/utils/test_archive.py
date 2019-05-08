import unittest
import tarfile
import os
from PyExpUtils.utils.archive import getArchiveName, inArchive

class TestArchive(unittest.TestCase):
    def test_getArchiveName(self):
        path = 'test/path/thing'

        got = getArchiveName(path)
        expected = 'test.tar'

        self.assertEqual(got, expected)

    def test_inArchive(self):
        with open('inArchive.txt', 'w') as f:
            f.write('hey there')

        with tarfile.open('inArchive.tar', 'w') as tar:
            tar.add('inArchive.txt')

        got = inArchive('inArchive.tar', 'inArchive.txt')
        self.assertTrue(got)

        got = inArchive('inArchive.tar', 'notInArchive.txt')
        self.assertFalse(got)

        got = inArchive('notAnArchive.tar', 'inArchive.txt')
        self.assertFalse(got)

        os.remove('inArchive.tar')
        os.remove('inArchive.txt')
