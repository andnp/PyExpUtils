import unittest
import pandas as pd
import tests._utils.pandas as pdu
from PyExpUtils.results.tools import subsetDF, splitByValue

class TestTools(unittest.TestCase):
    def test_subsetDF(self):
        df = pd.DataFrame({
            'a': [1, 1, 1, 2, 2],
            'b': [2, 4, 6, 8, 10],
        })

        # check base case
        sub = subsetDF(df, {})
        self.assertTrue(df.equals(sub))

        # check simple case where a single value is specified
        sub = subsetDF(df, { 'a': 2 })
        expect = pd.DataFrame({
            'a': [2, 2],
            'b': [8, 10],
        })
        self.assertTrue(sub.equals(expect))

        # check can specify multiple columns
        sub = subsetDF(df, {'a': 1, 'b': 4})
        expect = pd.DataFrame({
            'a': [1],
            'b': [4],
        })
        self.assertTrue(sub.equals(expect))

        # check can specify a list of values for a column
        sub = subsetDF(df, {'b': [4, 6, 8]})
        expect = pd.DataFrame({
            'a': [1, 1, 2],
            'b': [4, 6, 8],
        })
        self.assertTrue(sub.equals(expect))

        # check can specify non-existent columns
        sub = subsetDF(df, {'a': 1, 'c': 22})
        expect = pd.DataFrame({
            'a': [1, 1, 1],
            'b': [2, 4, 6],
        })
        self.assertTrue(sub.equals(expect))

    def test_splitByValue(self):
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 6],
            'b': [0, 0, 1, 1, 1, 2],
        })

        parts = list(splitByValue(df, 'b'))

        self.assertEqual(parts[0][0], 0)
        pdu.check_equal(parts[0][1], pd.DataFrame({
            'a': [1, 2],
            'b': [0, 0],
        }))

        self.assertEqual(parts[1][0], 1)
        pdu.check_equal(parts[1][1], pd.DataFrame({
            'a': [3, 4, 5],
            'b': [1, 1, 1],
        }))

        self.assertEqual(parts[2][0], 2)
        pdu.check_equal(parts[2][1], pd.DataFrame({
            'a': [6],
            'b': [2],
        }))
