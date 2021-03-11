import unittest
import os
import shutil
import tarfile
from PyExpUtils.results.paths import listResultsPaths, listMissingResults
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class RLExperiment(ExperimentDescription):
    def __init__(self, d):
        super().__init__(d)
        self.agent = d['agent']
        self.environment = d['environment']

class TestPaths(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree('.tmp')
            os.remove('.tmp.tar')
        except:
            pass

    def test_listResultsPaths(self):
        exp = RLExperiment({
            'agent': 'test_listResultsPaths',
            'environment': 'gridworld',
            'metaParameters': {
                'alpha': [0.01, 0.02],
                'lambda': [1.0, 0.99],
            }
        })

        got = list(listResultsPaths(exp, 2))
        expected = [
            '.tmp/test_listResultsPaths/gridworld/alpha-0.01_lambda-1.0/0',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.02_lambda-1.0/0',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.01_lambda-0.99/0',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.02_lambda-0.99/0',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.01_lambda-1.0/1',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.02_lambda-1.0/1',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.01_lambda-0.99/1',
            '.tmp/test_listResultsPaths/gridworld/alpha-0.02_lambda-0.99/1',
        ]

        self.assertListEqual(got, expected)

    def test_listMissingResults_files(self):
        exp = RLExperiment({
            'agent': 'test_listMissingResults_files',
            'environment': 'gridworld',
            'metaParameters': {
                'alpha': [0.01, 0.02],
                'lambda': [1.0, 0.99],
            }
        })

        mock_data = [
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.01_lambda-1.0/0',
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.01_lambda-1.0/1',
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.01_lambda-0.99/0',
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.02_lambda-1.0/0',
        ]

        for path in mock_data:
            os.makedirs(path, exist_ok=True)

        got = list(listMissingResults(exp, 2))
        expected = [
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.02_lambda-0.99/0',
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.02_lambda-1.0/1',
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.01_lambda-0.99/1',
            '.tmp/test_listMissingResults_files/gridworld/alpha-0.02_lambda-0.99/1',
        ]

        self.assertListEqual(got, expected)

    def test_listMissingResults_archive(self):
        key = '.tmp_test_listMissingResults_archive/{agent}/{environment}/{params}/{run}'
        exp = RLExperiment({
            'agent': 'test',
            'environment': 'gridworld',
            'metaParameters': {
                'alpha': [0.01, 0.02],
                'lambda': [1.0, 0.99],
            }
        })

        mock_data = [
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.01_lambda-1.0/1', # 4
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.01_lambda-1.0/0', # 0
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.01_lambda-0.99/0', # 1
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.02_lambda-1.0/0', # 2
        ]

        with tarfile.open('.tmp_test_listMissingResults_archive.tar', 'a') as tar:
            for path in mock_data:
                os.makedirs(path, exist_ok=True)
                tar.add(path)

            shutil.rmtree('.tmp_test_listMissingResults_archive/test')

        got = list(listMissingResults(exp, 2, key=key))
        expected = [
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.02_lambda-0.99/0',
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.02_lambda-1.0/1',
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.01_lambda-0.99/1',
            '.tmp_test_listMissingResults_archive/test/gridworld/alpha-0.02_lambda-0.99/1',
        ]


        self.assertListEqual(got, expected)
        os.remove('.tmp_test_listMissingResults_archive.tar')
        shutil.rmtree('.tmp_test_listMissingResults_archive')
