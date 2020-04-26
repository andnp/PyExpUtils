from typing import cast
import unittest
from PyExpUtils.utils.permute import PathDict, getNumberOfPermutations, getParameterPermutation, reconstructParameters

class TestPermute(unittest.TestCase):
    def test_getParameterPermutation(self):
        # base functionality
        d = {
            'alpha': [1.0, 0.5, 0.25, 0.125],
            'beta': [0.2, 0.4, 0.6],
        }

        got = getParameterPermutation(d, 0)
        expected = {
            'alpha': 1.0,
            'beta': 0.2,
        }
        self.assertDictEqual(got, expected)

        got = getParameterPermutation(d, 1)
        expected = {
            'alpha': 0.5,
            'beta': 0.2,
        }
        self.assertDictEqual(got, expected)

        got = getParameterPermutation(d, 4)
        expected = {
            'alpha': 1.0,
            'beta': 0.4,
        }
        self.assertDictEqual(got, expected)

        # nested objects
        d = {
            'alpha': [1.0, 0.5],
            'optimizer': {
                'type': ['SGD', 'SuperGood'],
                'beta': 0.1,
            }
        }

        got = getParameterPermutation(d, 0)
        expected = {
            'alpha': 1.0,
            'optimizer': {
                'type': 'SGD',
                'beta': 0.1,
            },
        }
        self.assertDictEqual(got, expected)

        got = getParameterPermutation(d, 2)
        expected = {
            'alpha': 1.0,
            'optimizer': {
                'type': 'SuperGood',
                'beta': 0.1,
            },
        }
        self.assertDictEqual(got, expected)

        # array of objects
        d = {
            'alpha': [1.0, 0.5],
            'layers': [
                { 'type': 'Linear', 'units': [2, 4, 8] },
                { 'type': 'Tanh', 'units': [2, 3, 4] },
            ],
        }

        got = getParameterPermutation(d, 0)
        expected = {
            'alpha': 1.0,
            'layers': [
                { 'type': 'Linear', 'units': 2 },
                { 'type': 'Tanh', 'units': 2 },
            ],
        }
        self.assertDictEqual(got, expected)

        got = getParameterPermutation(d, 2)
        expected = {
            'alpha': 1.0,
            'layers': [
                { 'type': 'Linear', 'units': 4 },
                { 'type': 'Tanh', 'units': 2 },
            ],
        }
        self.assertDictEqual(got, expected)

    def test_reconstructParameters(self):
        # can reconstruct nested objects from paths
        path_dict = cast(PathDict, {
            'metaParameters.alpha': 0.4,
            'metaParameters.beta': 0.2,
            'metaParameters.optimizer.type': 'SGD',
        })

        got = reconstructParameters(path_dict)
        expected = {
            'metaParameters': {
                'alpha': 0.4,
                'beta': 0.2,
                'optimizer': {
                    'type': 'SGD',
                },
            },
        }
        self.assertDictEqual(got, expected)

        # can reconstruct lists from paths
        path_dict = cast(PathDict, {
            'alpha': 0.1,
            'layers.[0].type': 'SGD',
        })

        got = reconstructParameters(path_dict)
        expected = {
            'alpha': 0.1,
            'layers': [
                { 'type': 'SGD' },
            ],
        }
        self.assertDictEqual(got, expected)

    def test_getNumberOfPermutations(self):
        d = {
            'alpha': [1, 2, 3],
            'beta': [4, 3, 2],
            'optimizers': {
                'type': 'momentum',
                'beta': [0.99, 0.98, 0.975],
            },
        }

        got = getNumberOfPermutations(d)
        expected = 27
        self.assertEqual(got, expected)
