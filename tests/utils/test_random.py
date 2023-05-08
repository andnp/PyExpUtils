import numba.typed
import unittest
import numpy as np
from PyExpUtils.utils.random import argmax, choice, sample

class TestRandom(unittest.TestCase):
    def test_sample(self):
        rng = np.random.default_rng(0)
        # base functionality
        arr = np.array([.50, .20, .10, .10, .10])

        got = sample(arr, rng)
        expected = 1 # an index from 0-4

        self.assertEqual(got, expected)

        arr = np.array([.01, .01, .08, .9])

        got = sample(arr, rng)
        expected = 3 # an index from 0-3

        self.assertEqual(got, expected)

    def test_choice(self):
        rng = np.random.default_rng(0)

        arr = numba.typed.List(['a', 'b', 'c'])

        got = choice(arr, rng)
        expected = 'c' # one of the three elements

        self.assertEqual(got, expected)

        counts = {'a': 0, 'b': 0, 'c': 0}
        for _ in range(10000):
            element = choice(arr, rng)
            counts[element] += 1

        # super fragile
        # TODO: make this a statistical test for uniformity
        self.assertDictEqual(counts, { 'a': 3309, 'b': 3389, 'c': 3302 })

    def test_argmax(self):
        rng = np.random.default_rng(0)

        arr = np.array([3, 2, 3])

        got = argmax(arr, rng)
        expected = 0 # either 0 or 2

        self.assertEqual(got, expected)

        counts = [0, 0, 0]
        for _ in range(10000):
            got = argmax(arr, rng)
            counts[got] += 1

        # TODO: make this a statistical test for uniformity
        self.assertEqual(counts, [4971, 0, 5029])
