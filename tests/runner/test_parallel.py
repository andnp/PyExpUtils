import unittest
from PyExpUtils.runner.parallel import build

class TestParallel(unittest.TestCase):
    def test_build(self):
        d = {
            'executable': 'thingDoer.exe',
            'cores': 22,
            'tasks': [1, 2, 3, 4, 5],
        }

        got = build(d)
        expected = 'parallel -j 22 thingDoer.exe ::: 1 2 3 4 5'
        self.assertEqual(got, expected)
