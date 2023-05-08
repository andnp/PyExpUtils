import unittest
from PyExpUtils.utils.cmdline import flagString

class TestCmdline(unittest.TestCase):
    def test_flagString(self):
        # base functionality
        pairs = [
            ('--test', 'a'),
            ('--trial', 'b'),
            ('--exam', 'c'),
        ]

        got = flagString(pairs)
        expected = '--exam=c --test=a --trial=b'

        self.assertEqual(got, expected)

        # removes None entries
        pairs = [
            ('--test', 'a'),
            ('--exam', None),
        ]

        got = flagString(pairs)
        expected = '--test=a'

        self.assertEqual(got, expected)

        # can join arguments with arbitrary string
        pairs = [
            ('--test', 'a'),
            ('--exam', 'b'),
        ]

        got = flagString(pairs, ' ')
        expected = '--exam b --test a'

        self.assertEqual(got, expected)
