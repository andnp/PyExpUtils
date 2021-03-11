from PyExpUtils.utils.arrays import first
from typing import List
import shutil
import os
import PyExpUtils.results.backends.h5 as H5Backend
from PyExpUtils.results.results import loadResults
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
        return '.tests/test_h5'

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

    def test_loadResults(self):
        dummy = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
        ])

        # --------------------------
        # Can save h5 data to a file
        # --------------------------
        exp = ExperimentDescription({ "metaParameters": { 'alpha': 0.01 } }, save_key='')

        base = f'{self.getBase()}/test_loadResults'

        path = ''
        num_params = exp.numPermutations()
        for i in range(3):
            path = H5Backend.saveResults(exp, i * num_params, 'test1', dummy[i], base=base)

        self.registerFile(path)

        results = H5Backend.loadResults(exp, 'test1.h5', base=base, cache=False)
        results = list(results)
        result = results[0]

        got = result.load()
        self.assertTrue(np.allclose(got, dummy))

        got = result.mean()
        expected = np.array([2, 3, 4, 5, 6])
        self.assertTrue(np.allclose(got, expected))

        # ----------------------
        # Can handle uneven data
        # ----------------------
        uneven_dummy = [
            np.array([1., 2, 3]),
            np.array([2., 2]),
            np.array([3.]),
        ]

        path = H5Backend.saveSequentialRuns(exp, 0, 'test2', uneven_dummy, base=base)
        self.registerFile(path)

        results = H5Backend.loadResults(exp, 'test2.h5', base=base)
        results = list(results)

        result = results[0]
        got = result.mean()
        expected = np.array([2, 2, 3])

        self.assertTrue(np.allclose(got, expected))

        # ------------------------
        # Can save multiple params
        # ------------------------
        dummy2 = dummy + 1

        exp = ExperimentDescription({ "metaParameters": { 'alpha': [0.01, 0.02] } }, save_key='')

        path = H5Backend.saveSequentialRuns(exp, 0, 'test3', dummy, base=base)
        path = H5Backend.saveSequentialRuns(exp, 1, 'test3', dummy2, base=base)
        self.registerFile(path)

        results = H5Backend.loadResults(exp, 'test3.h5', base=base)
        results = list(results)

        # check first result (alpha=0.01)
        result1 = results[0]

        got = result1.load()
        self.assertTrue(np.allclose(got, dummy))

        got = result1.mean()
        expected = np.array([2, 3, 4, 5, 6])
        self.assertTrue(np.allclose(got, expected))

        # check second result (alpha=0.02)
        result2 = results[1]

        got = result2.load()
        self.assertTrue(np.allclose(got, dummy2))

        got = result2.mean()
        expected = np.array([3, 4, 5, 6, 7])
        self.assertTrue(np.allclose(got, expected))
