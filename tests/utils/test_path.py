import unittest
from PyExpUtils.utils.path import rest

class TestPath(unittest.TestCase):
    def test_rest(self):
        test_path = 'this/is/a/test'

        got = rest(test_path)
        expected = 'is/a/test'

        self.assertEqual(got, expected)

        test_path = '/this/is/a/test'

        got = rest(test_path)
        expected = 'this/is/a/test'

        self.assertEqual(got, expected)
