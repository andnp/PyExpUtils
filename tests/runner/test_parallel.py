import unittest
from PyExpUtils.runner.parallel import build, flagString

class TestParallel(unittest.TestCase):
    def test_flagString(self):
        pairs = [
            ('-j', 22),
            ('--delay', 1),
        ]

        got = flagString(pairs)
        expected = '-j 22 --delay 1'
        self.assertEqual(got, expected)

        # drop None values
        pairs = [
            ('-j', 22),
            ('--delay', None),
        ]

        got = flagString(pairs)
        expected = '-j 22'
        self.assertEqual(got, expected)

    def test_build(self):
        d = {
            'executable': 'thingDoer.exe',
            'cores': 22,
            'tasks': [1, 2, 3, 4, 5],
        }

        got = build(d)
        expected = 'parallel -j 22 thingDoer.exe ::: 1 2 3 4 5'
        self.assertEqual(got, expected)
