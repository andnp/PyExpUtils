from PyExpUtils.utils.arrays import first
from typing import List
import shutil
import os
from PyExpUtils.results.backends.backend import BaseResult
import PyExpUtils.results.backends.csv as CsvBackend
from PyExpUtils.results.results import loadResults, whereParametersEqual, splitOverParameter
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
    files: List[str] = []

    def getBase(self):
        return '.tests/test_results'

    def registerFile(self, name: str):
        rest = os.path.dirname(name)
        os.makedirs(rest, exist_ok=True)
        self.files.append(name)

    @classmethod
    def tearDownClass(cls) -> None:
        for name in cls.files:
            di = name.split('/')[0]
            shutil.rmtree(di, ignore_errors=True)

        return super().tearDownClass()

    def test_Results(self):
        results = [BaseResult('fake/path', exp, i) for i in listIndices(exp)]

        r = results[0]
        self.assertDictEqual(r.params, { 'alpha': 1.0, 'ratio': 1.0, 'model': { 'name': 'PR' }})
        r = results[1]
        self.assertDictEqual(r.params, { 'alpha': 0.5, 'ratio': 1.0, 'model': { 'name': 'PR' }})
        self.assertEqual(r.idx, 1)

    def test_splitOverParameter(self):
        results = (BaseResult('fake/path', exp, i) for i in listIndices(exp))

        split_results = splitOverParameter(results, 'alpha')
        self.assertEqual(list(split_results), [1.0, 0.5, 0.25]) # check keys
        self.assertEqual(len(split_results[1.0]), 8)

        for key in split_results:
            sub_results = split_results[key]
            for res in sub_results:
                self.assertEqual(res.params['alpha'], key)

        results = (BaseResult('fake/path', exp, i) for i in listIndices(exp))

        split_results = splitOverParameter(results, 'model.name')
        self.assertEqual(list(split_results), ['PR', 'ESARSA']) # check keys
        self.assertEqual(len(split_results['PR']), 12)

    def test_whereParametersEqual(self):
        results = (BaseResult('fake/path', exp, i) for i in listIndices(exp))

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

    def test_loadResults(self):
        dummy = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
        ])

        # ------------------------------------------
        # Can automatically infer CSV data from file
        # ------------------------------------------
        exp = ExperimentDescription({ "metaParameters": { 'alpha': 0.01 } }, save_key='{params}')

        base = f'{self.getBase()}/test_loadResults'

        path = ''
        for i, data in enumerate(dummy):
            path = CsvBackend.saveResults(exp, i, 'test3', data, base=base)

        self.registerFile(path)

        results = loadResults(exp, 'test3.csv', base=base)
        result = first(results)

        got = result.mean()
        expected = np.array([2, 3, 4, 5, 6])
        self.assertTrue(np.allclose(got, expected))

        # -------------------------------------------
        # Can automatically infer CSV data from class
        # -------------------------------------------
        class DummyCsv(CsvBackend.Result):
            pass

        exp = ExperimentDescription({ "metaParameters": { 'alpha': 0.01 } }, save_key='{params}')

        base = f'{self.getBase()}/test_loadResults'

        for i, data in enumerate(dummy):
            path = CsvBackend.saveResults(exp, i, 'test4.dat', data, base=base)

        self.registerFile(path)

        results = loadResults(exp, 'test4.dat', base=base, ResultClass=DummyCsv)
        result = first(results)

        got = result.mean()
        expected = np.array([2, 3, 4, 5, 6])
        self.assertTrue(np.allclose(got, expected))
