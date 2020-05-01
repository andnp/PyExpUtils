import unittest
import numpy as np
from PyExpUtils.utils.random import argmax, choice, sample
class TestRandom(unittest.TestCase):
    def test_sample(self):
        np.random.seed(0)
        # base functionality
        arr = [.50, .20, .10, .10, .10]

        got = sample(arr)
        expected = 1 # an index from 0-4

        self.assertEqual(got, expected)

        arr = [.01, .01, .08, .9]

        got = sample(arr)
        expected = 3 # an index from 0-3

        self.assertEqual(got, expected)

    def test_choice(self):
        np.random.seed(0)

        arr = ['a', 'b', 'c']

        got = choice(arr)
        expected = 'c' # one of the three elements

        self.assertEqual(got, expected)

        counts = {'a': 0, 'b': 0, 'c': 0}
        for _ in range(10000):
            element = choice(arr)
            counts[element] += 1

        # super fragile
        # TODO: make this a statistical test for uniformity
        self.assertDictEqual(counts, { 'a': 3313, 'b': 3304, 'c': 3383 })

    def test_argmax(self):
        np.random.seed(0)

        arr = [3, 2, 3]

        got = argmax(arr)
        expected = 2 # either 0 or 2

        self.assertEqual(got, expected)

        counts = [0, 0, 0]
        for _ in range(10000):
            got = argmax(arr)
            counts[got] += 1

        # TODO: make this a statistical test for uniformity
        self.assertEqual(counts, [5086, 0, 4914])

        # return nan values
        arr = [np.nan, np.nan, 3]

        got = argmax(arr)
        expected = 0 # either 0 or 1

        self.assertEqual(got, expected)
