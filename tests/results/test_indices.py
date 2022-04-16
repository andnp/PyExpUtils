import unittest
import os
import shutil
from PyExpUtils.results.indices import listIndices
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class RLExperiment(ExperimentDescription):
    def __init__(self, d):
        super().__init__(d)
        self.agent = d['agent']
        self.environment = d['environment']

class TestIndices(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree('.tmp')
            os.remove('.tmp.tar')
        except:
            pass

    def test_listIndices(self):
        exp = ExperimentDescription({
            'metaParameters': {
                'alpha': [0.01, 0.02, 0.04, 0.08, 0.16],
                'lambda': [1.0, 0.99, 0.98, 0.96, 0.92],
            }
        })

        expected = list(range(25))
        got = list(listIndices(exp))

        self.assertListEqual(got, expected)
