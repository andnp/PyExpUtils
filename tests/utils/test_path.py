import unittest
from PyExpUtils.utils.path import fileName, join, rest, up

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

    def test_up(self):
        test_path = 'this/is/a/test'

        got = up(test_path)
        expected = 'this/is/a'
        self.assertEqual(got, expected)

        test_path = '/this/is/a/test'

        got = up(test_path)
        expected = '/this/is/a'
        self.assertEqual(got, expected)

    def test_fileName(self):
        test_path = 'this/is/a/test'

        got = fileName(test_path)
        expected = 'test'
        self.assertEqual(got, expected)

        test_path = '/this/is/a/test.txt'

        got = fileName(test_path)
        expected = 'test.txt'
        self.assertEqual(got, expected)

        test_path = 'test.txt'

        got = fileName(test_path)
        expected = 'test.txt'
        self.assertEqual(got, expected)

    def test_join(self):
        test_parts = ['/this', 'is', 'a/', 'test']

        got = join(*test_parts)
        expected = '/this/is/a/test'
        self.assertEqual(got, expected)

        test_parts = ['this', '//is/', '/a/', 'test/']

        got = join(*test_parts)
        expected = 'this/is/a/test'
        self.assertEqual(got, expected)

        test_parts = ['this/is', 'a', 'test']

        got = join(*test_parts)
        expected = 'this/is/a/test'
        self.assertEqual(got, expected)
