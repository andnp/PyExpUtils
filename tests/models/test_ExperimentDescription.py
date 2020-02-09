import unittest
import os
from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment

class TestSavingPath(unittest.TestCase):
    def test_path(self):
        desc = {
            'name': 'test',
            'algorithm': 'q',
            'environment': 'mountaincar',
            'metaParameters': {
                'alpha': [0.01, 0.02],
                'epsilon': 0.05,
            }
        }

        class MLExpDesc(ExperimentDescription):
            def __init__(self, d):
                super().__init__(d)
                self.algorithm = d['algorithm']
                self.env = d['environment']

        exp = MLExpDesc(desc)
        key = '{name}/{algorithm}/{env}/{params}/{run}'

        got = exp.interpolateSavePath(0, key=key)
        expected = 'test/q/mountaincar/alpha-0.01_epsilon-0.05/0'
        self.assertEqual(got, expected)

class TestPermutations(unittest.TestCase):
    def fakeDescription(self):
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

    def test_permutable(self):
        desc = self.fakeDescription()
        exp = ExperimentDescription(desc)

        # permutable defaults to 'metaParameters' being the only permutable key
        got = exp.permutable()
        self.assertDictEqual(
            got,
            {
                'metaParameters': desc['metaParameters']
            },
        )

        # can specify a list of parameters to permute over
        got = exp.permutable(['metaParameters', 'envParameters'])
        self.assertDictEqual(
            got,
            desc
        )

    def test_getPermutations(self):
        desc = self.fakeDescription()
        exp = ExperimentDescription(desc)

        # can get permutation of metaParameters by default
        got = exp.getPermutation(0)
        expected = desc.copy()
        expected['metaParameters'] = {
            'alpha': 0.01,
            'epsilon': 0.05,
            'gamma': 0.9,
        }
        self.assertDictEqual(
            got,
            expected,
        )

        # can get permutation of multiple parameters
        got = exp.getPermutation(0, keys=['metaParameters', 'envParameters'])
        expected = {
            'metaParameters': {
                'alpha': 0.01,
                'epsilon': 0.05,
                'gamma': 0.9,
            },
            'envParameters': {
                'size': 30,
                'noise': 0.01,
            },
        }
        self.assertDictEqual(got, expected)

    def test_permutations(self):
        desc = self.fakeDescription()
        exp = ExperimentDescription(desc)

        # compute number of permutations first time
        got = exp.numPermutations()
        expected = 3
        self.assertEqual(got, expected)

        # recompute if the keys are different
        got = exp.numPermutations(keys='envParameters')
        expected = 2
        self.assertEqual(got, expected)

        # recompute if keys is array
        got = exp.numPermutations(keys=['metaParameters', 'envParameters'])
        expected = 6
        self.assertEqual(got, expected)

class TestExperimentName(unittest.TestCase):
    def test_fromFile(self):
        exp = loadExperiment('mock_repo/experiments/overfit/best/ann.json')

        got = exp.getExperimentName()
        expected = 'overfit/best'

        self.assertEqual(got, expected)

    def test_withCWD(self):
        exp = loadExperiment(f'{os.getcwd()}/mock_repo/experiments/overfit/best/ann.json')

        got = exp.getExperimentName()
        expected = 'overfit/best'

        self.assertEqual(got, expected)

    def test_withDotSlash(self):
        exp = loadExperiment('./mock_repo/experiments/overfit/best/ann.json')

        got = exp.getExperimentName()
        expected = 'overfit/best'

        self.assertEqual(got, expected)
