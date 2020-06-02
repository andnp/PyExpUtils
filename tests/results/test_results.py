from PyExpUtils.results.results import Result, whereParametersEqual, getBest, splitOverParameter
from PyExpUtils.results.indices import listIndices
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
import unittest
import numpy as np

exp = ExperimentDescription({
    'metaParameters': {
        'alpha': [1.0, 0.5, 0.25],
        'ratio': [1.0, 2.0, 4.0, 8.0],
        'model': {
            'name': ['PR', 'ESARSA'],
        }
    },
})

class TestResults(unittest.TestCase):
    def test_Results(self):
        results = [Result('fake/path', exp, i) for i in listIndices(exp)]

        r = results[0]
        self.assertDictEqual(r.params, { 'alpha': 1.0, 'ratio': 1.0, 'model': { 'name': 'PR' }})
        r = results[1]
        self.assertDictEqual(r.params, { 'alpha': 0.5, 'ratio': 1.0, 'model': { 'name': 'PR' }})
        self.assertEqual(r.idx, 1)

        # can overload load function
        class TestResult(Result):
            def _load(self):
                # (mean, std, runs)
                return (1, 2, 3)

        results = [TestResult('fake/path', exp, i) for i in listIndices(exp)]

        r = results[0]
        self.assertEqual(r.mean(), 1)


    def test_splitOverParameter(self):
        results = (Result('fake/path', exp, i) for i in listIndices(exp))

        split_results = splitOverParameter(results, 'alpha')
        self.assertEqual(list(split_results), [1.0, 0.5, 0.25]) # check keys
        self.assertEqual(len(split_results[1.0]), 8)

        for key in split_results:
            sub_results = split_results[key]
            for res in sub_results:
                self.assertEqual(res.params['alpha'], key)

        results = (Result('fake/path', exp, i) for i in listIndices(exp))

        split_results = splitOverParameter(results, 'model.name')
        self.assertEqual(list(split_results), ['PR', 'ESARSA']) # check keys
        self.assertEqual(len(split_results['PR']), 12)


    def test_getBest(self):
        # lowest
        load_counter = 0
        class TestResult(Result):
            def _load(self):
                nonlocal load_counter
                load_counter += 1
                return (np.ones(100) * load_counter, np.ones(100), 3)

        results = (TestResult('fake/path', exp, i) for i in listIndices(exp))

        best = getBest(results)
        self.assertEqual(best.mean()[0], 1)

        # highest
        results = (TestResult('fake/path', exp, i) for i in listIndices(exp))

        best = getBest(results, comparator=lambda a, b: a > b)
        self.assertEqual(best.mean()[0], load_counter)

    def test_whereParametersEqual(self):
        results = (Result('fake/path', exp, i) for i in listIndices(exp))

        results = whereParametersEqual(results, {
            'alpha': 1.0,
            'epsilon': 2, # if a parameter in the filter list does not exist, ignore it
            'model': {
                'name': 'ESARSA',
            },
        })
        results = list(results)

        self.assertEqual(len(results), 4)

        got = [r.params['ratio'] for r in results]
        expected = [1.0, 2.0, 4.0, 8.0]
        self.assertListEqual(got, expected)
