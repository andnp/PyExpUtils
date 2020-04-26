import unittest
from PyExpUtils.utils.arrays import fillRest, first, last, partition

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
