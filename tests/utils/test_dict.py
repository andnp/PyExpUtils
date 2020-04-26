from PyExpUtils.utils.dict import equal, hyphenatedStringify, merge, pick
import unittest

class TestDict(unittest.TestCase):
    def test_merge(self):
        # base functionality
        d1 = {
            'a': [1, 2, 3],
            'b': False,
            'c': {
                'aa': [4, 5, 6],
            },
        }

        d2 = {
            'b': True,
            'd': 22,
        }

        got = merge(d1, d2)
        expected = {
            'a': [1, 2, 3],
            'b': True,
            'c': {
                'aa': [4, 5, 6],
            },
            'd': 22,
        }

        self.assertDictEqual(got, expected)

    def test_hyphenateStringify(self):
        # base functionality
        d = {
            'alpha': 0.1,
            'beta': 0.99,
            'gamma': 1,
            'optimizer': 'SuperFast',
        }

        got = hyphenatedStringify(d)
        expected = 'alpha-0.1_beta-0.99_gamma-1_optimizer-SuperFast'

        self.assertEqual(got, expected)

        # keys are sorted alphabetically
        d = {
            'beta': 0.95,
            'alpha': -0.5,
        }

        got = hyphenatedStringify(d)
        expected = 'alpha--0.5_beta-0.95'

        self.assertEqual(got, expected)

    def test_pick(self):
        # base functionality
        d = {
            'a': 1,
            'b': 22,
            'c': 333,
        }

        got = pick(d, 'a')
        expected = 1

        self.assertEqual(got, expected)

        # multiple keys
        d = {
            'a': 1,
            'b': 22,
            'c': 333,
        }

        got = pick(d, ['a', 'b'])
        expected = {
            'a': 1,
            'b': 22,
        }

        self.assertDictEqual(got, expected)

    def test_equal(self):
        # base functionality
        d1 = {
            'a': [1, 2, 3],
            'b': 'a',
            'c': {
                'aa': 22,
            },
        }

        d2 = {
            'a': [1, 2, 3],
            'b': 'a',
            'c': {
                'aa': 22,
            },
        }

        got = equal(d1, d2)
        self.assertTrue(got)

        # missing keys
        d1 = {
            'a': 22,
            'b': 'a',
        }

        d2 = {
            'a': 22,
        }

        got = equal(d1, d2)
        self.assertFalse(got)

        # ignore keys
        d1 = {
            'a': 22,
            'b': 'a',
        }

        d2 = {
            'a': 22,
        }

        got = equal(d1, d2, ['b'])
        self.assertTrue(got)

        # d1 missing keys
        d1 = {
            'a': 22,
        }

        d2 = {
            'a': 22,
            'b': 'a',
        }

        got = equal(d1, d2)
        self.assertTrue(got)
