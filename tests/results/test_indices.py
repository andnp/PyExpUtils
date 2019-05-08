import unittest
import os
import shutil
import tarfile
from PyExpUtils.results.indices import listIndices, listMissingResults
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

    def test_listMissingResults(self):
        exp = RLExperiment({
            'agent': 'test_files',
            'environment': 'gridworld',
            'metaParameters': {
                'alpha': [0.01, 0.02],
                'lambda': [1.0, 0.99],
            }
        })

        mock_data = [
            '.tmp/test_files/gridworld/alpha-0.01_lambda-1.0/0', # 0
            '.tmp/test_files/gridworld/alpha-0.01_lambda-1.0/1', # 4
            '.tmp/test_files/gridworld/alpha-0.01_lambda-0.99/0', # 1
            '.tmp/test_files/gridworld/alpha-0.02_lambda-1.0/0', # 2
        ]

        for path in mock_data:
            os.makedirs(path, exist_ok=True)

        got = list(listMissingResults(exp, 2))
        expected = [3, 5, 6, 7]

        self.assertListEqual(got, expected)

    def test_listMissingResultsArchive(self):
        exp = RLExperiment({
            'agent': 'test_archive',
            'environment': 'gridworld',
            'metaParameters': {
                'alpha': [0.01, 0.02],
                'lambda': [1.0, 0.99],
            }
        })

        mock_data = [
            'test_archive/gridworld/alpha-0.01_lambda-1.0/0', # 0
            'test_archive/gridworld/alpha-0.01_lambda-1.0/1', # 4
            'test_archive/gridworld/alpha-0.01_lambda-0.99/0', # 1
            'test_archive/gridworld/alpha-0.02_lambda-1.0/0', # 2
        ]

        with tarfile.open('.tmp.tar', 'a') as tar:
            for path in mock_data:
                os.makedirs(path, exist_ok=True)
                tar.add(path)

            shutil.rmtree('test_archive')

        got = list(listMissingResults(exp, 2))
        expected = [3, 5, 6, 7]

        self.assertListEqual(got, expected)
