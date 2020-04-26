import unittest
from PyExpUtils.utils.str import interpolate

class TestStr(unittest.TestCase):
    def test_interpolate(self):
        key = 'results/{name}/{run}/data'
        d = {
            'name': 'johnny',
            'run': 0,
        }

        got = interpolate(key, d)
        expected = 'results/johnny/0/data'

        self.assertEqual(got, expected)
