import unittest
import numba.typed as typed
from PyExpUtils.utils.arrays import argsmax, deduplicate, downsample, fillRest, first, last, partition, sampleFrequency

class TestArrays(unittest.TestCase):
    def test_fillRest(self):
        # base functionality
        arr = [1, 2, 3, 4]

        got = fillRest(arr, 5, 10)
        expected = [1, 2, 3, 4, 5, 5, 5, 5, 5, 5] # length 10

        self.assertEqual(got, expected)

        # degenerate length
        arr = [1, 2, 3, 4]

        got = fillRest(arr, 5, 2)
        expected = [1, 2, 3, 4]

        self.assertEqual(got, expected)

    def test_first(self):
        # lists
        arr = [1, 2, 3, 4]

        got = first(arr)
        expected = 1

        self.assertEqual(got, expected)

        # iterators
        arr = ['a', 'b', 'c']
        it = arr.__iter__()

        got = first(it)
        expected = 'a'

        self.assertEqual(got, expected)

    def test_last(self):
        # base functionality
        arr = [1, 2, 3, 4]

        got = last(arr)
        expected = 4

        self.assertEqual(got, expected)

    def test_partition(self):
        # lists
        arr = [1, 2, 3, 4, 5, 6]

        l, r = partition(arr, lambda a: a > 3)
        self.assertEqual(list(l), [4, 5, 6])
        self.assertEqual(list(r), [1, 2, 3])

        # iterators
        arr = [1, 2, 3, 4, 5, 6]
        it = arr.__iter__()

        l, r = partition(it, lambda a: a > 3)
        self.assertEqual(list(l), [4, 5, 6])
        self.assertEqual(list(r), [1, 2, 3])

    def test_deduplicate(self):
        arr = [1, 2, 3, 2, 5, 7, 1, 2, 3]

        got = deduplicate(arr)
        expected = [1, 2, 3, 5, 7]

        # note that order isn't guaranteed so this is a brittle test...
        # maybe should fix this later
        self.assertListEqual(got, expected)

    def test_sampleFrequency(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        got = sampleFrequency(arr, percent=.1)
        expected = 10

        self.assertEqual(expected, got)

        got = sampleFrequency(arr, percent=.23)
        expected = 5

        self.assertEqual(expected, got)

        got = sampleFrequency(arr, num=4)
        expected = 2

        self.assertEqual(expected, got)

    def test_downsample(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        got = downsample(arr, percent=0.23, method='window')
        expected = [3, 8]

        self.assertEqual(got, expected)

        got = downsample(arr, num=3, method='window')
        expected = [2, 5, 8]

        self.assertEqual(got, expected)

        got = downsample(arr, percent=0.23, method='subsample')
        expected = [1, 6]

        self.assertEqual(got, expected)

        got = downsample(arr, num=4, method='subsample')
        expected = [2, 4, 6, 8]

    def test_argsmax(self):
        arr = typed.List([0, 0, 1, 2])

        got = argsmax(arr)
        expected = [3]

        self.assertEqual(got, expected)

        arr = typed.List([0, 2, 1, 2])

        got = argsmax(arr)
        expected = [1, 3]

        self.assertEqual(got, expected)
