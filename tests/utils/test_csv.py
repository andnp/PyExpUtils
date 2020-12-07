from PyExpUtils.utils.csv import arrayToCsv, buildCsvHeader, buildCsvParams
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
import unittest
import numpy as np

class TestCsv(unittest.TestCase):
    def fakeDoubleDescription(self):
        return {
            'metaParameters': {
                'alpha': [0.01, 0.02, 0.04],
                'epsilon': 0.05,
                'gamma': [0.9]
            },
            'envParameters': {
                'size': 30,
                'noise': [0.01, 0.02],
            }
        }

    def fakeDescription(self):
        return {
            'metaParameters': {
                'alpha': [0.01, 0.02, 0.04],
                'epsilon': 0.05,
                'gamma': [0.9]
            }
        }

    def test_buildCsvParams(self):
        exp = ExperimentDescription(self.fakeDescription())

        got = buildCsvParams(exp, 0)
        expected = '0.01,0.05,0.9'

        self.assertEqual(got, expected)

        exp = ExperimentDescription(self.fakeDoubleDescription(), keys=['metaParameters', 'envParameters'])

        got = buildCsvParams(exp, 1)
        expected = '0.02,30,0.01,0.05,0.9'

        self.assertEqual(got, expected)

    def test_buildCsvHeader(self):
        exp = ExperimentDescription(self.fakeDescription())

        got = buildCsvHeader(exp)
        expected = 'alpha,epsilon,gamma'

        self.assertEqual(got, expected)

        exp = ExperimentDescription(self.fakeDoubleDescription(), keys=['metaParameters', 'envParameters'])

        got = buildCsvHeader(exp)
        expected = 'envParameters.noise,envParameters.size,metaParameters.alpha,metaParameters.epsilon,metaParameters.gamma'

        self.assertEqual(got, expected)

    def test_arrayToCsv(self):
        data = np.arange(5) / 4

        got = arrayToCsv(data, 1)
        expected = '0.0,0.2,0.5,0.8,1.0'

        self.assertEqual(got, expected)
