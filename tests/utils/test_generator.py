from PyExpUtils.utils.generator import group, windowAverage
import unittest

class TestGenerator(unittest.TestCase):
    def test_group(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8]

        got = list(group(arr, 3))
        expected = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8], # last group may not be same size as rest
        ]

        self.assertEqual(got, expected)

    def test_windowAverage(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8]

        got = list(windowAverage(arr, 3))
        expected = [2, 5, 7.5]

        self.assertEqual(got, expected)
