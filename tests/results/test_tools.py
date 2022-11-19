import unittest
import pandas as pd
from PyExpUtils.results.tools import subsetDF

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
