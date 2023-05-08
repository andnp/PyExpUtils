from typing import List
import shutil
import os
import PyExpUtils.results.pandas as PDBackend
from PyExpUtils.results.tools import collapseRuns
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
import unittest
import pandas as pd
import numpy as np

from PyExpUtils.utils.Collector import Collector

class TestPandas(unittest.TestCase):
    files: List[str] = []

    def getBase(self):
        return '.tests/test_pandas'

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
        np.random.seed(0)
        dummy = np.random.normal(0, 1, size=(5000, 5))

        # --------------------------
        # Can save pd data to a file
        # --------------------------
        exp = ExperimentDescription({ "metaParameters": { 'alpha': 0.01 } }, save_key='')

        base = f'{self.getBase()}/test_loadResults'

        path = ''
        num_params = exp.numPermutations()
        for i in range(dummy.shape[0]):
            path = PDBackend.saveResults(exp, i * num_params, 'test1', dummy[i], base=base, batch_size=100)

        self.registerFile(path)

        df = PDBackend.loadResults(exp, 'test1', base=base, use_cache=False)
        data = np.array([np.asarray(row) for row in df['data']])

        got = data.mean(axis=0)
        expected = np.array([-0.01047754, 0.02722873, -0.0084752, -0.01217733, -0.0069713])
        self.assertTrue(np.allclose(got, expected, atol=1e-4))

        # ----------------------
        # Can handle uneven data
        # ----------------------
        uneven_dummy = [
            np.array([1., 2, 3]),
            np.array([2., 2]),
            np.array([3.]),
        ]

        path = PDBackend.saveSequentialRuns(exp, 0, 'test2', uneven_dummy, base=base)
        self.registerFile(path)

        df = PDBackend.loadResults(exp, 'test2', base=base)
        data = np.array([np.asarray(row) for row in df['data']])

        got = np.nanmean(data, axis=0)
        expected = np.array([2, 2, 3])

        self.assertTrue(np.allclose(got, expected))

        # check folding uneven runs
        df = collapseRuns(df)
        data = df['data'][0]

        got = np.nanmean(data, axis=0)
        expected = np.array([2, 2, 3])
        self.assertTrue(np.allclose(got, expected))

        # ------------------------
        # Can save multiple params
        # ------------------------
        dummy1 = dummy[:2500]
        dummy2 = dummy[2500:] + 1

        exp = ExperimentDescription({ "metaParameters": { 'alpha': [0.01, 0.02] } }, save_key='')

        path = PDBackend.saveSequentialRuns(exp, 0, 'test3', dummy1, base=base)
        path = PDBackend.saveSequentialRuns(exp, 1, 'test3', dummy2, base=base)
        self.registerFile(path)

        df = PDBackend.loadResults(exp, 'test3', base=base)
        data = np.array([np.asarray(row) for row in df['data']])

        # check first result (alpha=0.01)
        got = df[df['alpha'] == 0.01]['data']
        self.assertEqual(len(got), 2500)

        data = np.array([np.asarray(row) for row in got])
        got = np.mean(data, axis=0)
        expected = np.array([-0.02774155, 0.00835112, -0.03870346, -0.02883856, -0.00441377])
        self.assertTrue(np.allclose(got, expected, atol=1e-4))

        # check second result (alpha=0.02)
        got = df[df['alpha'] == 0.02]['data']
        self.assertEqual(len(got), 2500)

        data = np.array([np.asarray(row) for row in got])
        got = np.mean(data, axis=0)
        expected = np.array([1.00678647, 1.04610634, 1.02175261, 1.0044839, 0.99047117])
        self.assertTrue(np.allclose(got, expected, atol=1e-4))

    def test_saveCollector(self):
        collector = Collector()

        exp = ExperimentDescription({
            'metaParameters': {
                'alpha': [1.0, 0.5, 0.25],
                'ratio': [1.0, 2.0, 4.0, 8.0],
                'model': {
                    'name': ['PR', 'ESARSA'],
                }
            },
        }, save_key='')

        for idx in range(250):
            collector.setIdx(idx)

            for step in range(10):
                collector.collect('data1', idx + step)
                collector.concat('data2', [idx + step, idx + step * 1])

            collector.collect('data3', np.arange(5) * idx)

        base = f'{self.getBase()}/test_saveCollector'
        self.registerFile(base)
        PDBackend.saveCollector(exp, collector, base=base, batch_size=47)

        df1 = PDBackend.loadResults(exp, 'data1', base=base)
        df2 = PDBackend.loadResults(exp, 'data2', base=base)
        df3 = PDBackend.loadResults(exp, 'data3', base=base)
        self.assertEqual(len(df1), 250)
        self.assertEqual(len(df2), 250)
        self.assertEqual(len(df3), 250)

        self.assertEqual(set(df1['run']), set(range(11)))
        self.assertEqual(set(df2['run']), set(range(11)))
        self.assertEqual(set(df3['run']), set(range(11)))

        header = PDBackend.getHeader(exp)
        key = header + ['run']
        for idx in range(250):
            expected = [idx + j for j in range(10)]

            pvalues = PDBackend.getParamValues(exp, idx, header)
            val = pvalues + [exp.getRun(idx)]

            data = df1[(df1[key] == val).all(axis=1)]['data'].to_list()[0]
            self.assertEqual(data, expected)

    def test_detectMissingResults(self):
        base = f'{self.getBase()}/test_detectMissingResults'

        dummy = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
        ])

        dummy2 = [
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            None,
            [3, 4, 5, 6, 7],
        ]

        exp = ExperimentDescription({ "metaParameters": { 'alpha': [0.01, 0.02, 0.03, 0.04] } }, save_key='')

        path = PDBackend.saveSequentialRuns(exp, 0, 'test1', dummy, base=base)
        path = PDBackend.saveSequentialRuns(exp, 2, 'test1', dummy2, base=base)
        self.registerFile(path)

        missing = PDBackend.detectMissingIndices(exp, 5, 'test1', base=base)
        missing = list(missing)
        # no guarantees about ordering
        missing = sorted(missing)

        expected = [1, 3, 5, 7, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19]
        self.assertEqual(missing, expected)

    # -----------------
    # -- Regressions --
    # -----------------
    def test_loadsOnlySpecifiedParamValues(self):
        base = f'{self.getBase()}/test_loadsOnlySpecifiedParamValues'
        self.registerFile(base)

        collector = Collector()
        collector.setIdx(0)
        collector.concat('test1', [1, 2, 3])
        collector.setIdx(1)
        collector.concat('test1', [2, 3, 4])
        collector.setIdx(2)
        collector.concat('test1', [3, 4, 5])
        collector.setIdx(3)
        collector.concat('test1', [4, 5, 6])

        exp = ExperimentDescription({ 'metaParameters': { 'alpha': [0.1, 0.2, 0.3, 0.4] }}, save_key='')
        PDBackend.saveCollector(exp, collector, base=base)

        # assert we can load the complete thing correctly
        loaded = PDBackend.loadResults(exp, 'test1', base=base, use_cache=False)
        expected = pd.DataFrame({
            'alpha': [0.1, 0.2, 0.3, 0.4],
            'run': [0, 0, 0, 0],
            'data': [
                [1, 2, 3],
                [2, 3, 4],
                [3, 4, 5],
                [4, 5, 6],
            ]
        })
        self.assertTrue(loaded.equals(expected))

        # assert we can load a subset
        sub_exp = ExperimentDescription({ 'metaParameters': { 'alpha': [0.2, 0.3] }}, save_key='')
        loaded = PDBackend.loadResults(sub_exp, 'test1', base=base, use_cache=False)
        expected = pd.DataFrame({
            'alpha': [0.2, 0.3],
            'run': [0, 0],
            'data': [
                [2, 3, 4],
                [3, 4, 5],
            ],
        })
        self.assertTrue(loaded.equals(expected))

    def test_canHandleListsOfDicts(self):
        exp = ExperimentDescription({
            'metaParameters': {
                'alpha': [0.1, 0.01],
                'network': {
                    'layers': [
                        { 'units': 64 },
                        { 'units': 32 },
                    ]
                }
            }
        }, save_key='')

        base = f'{self.getBase()}/test_canHandleListsofDicts'
        self.registerFile(base)

        collector = Collector()
        collector.setIdx(0)
        collector.concat('test1', [1, 2, 3])
        collector.setIdx(2)
        collector.concat('test1', [3, 4, 5])
        collector.setIdx(3)
        collector.concat('test1', [4, 5, 6])

        PDBackend.saveCollector(exp, collector, base=base)
        missing = list(PDBackend.detectMissingIndices(exp, 2, 'test1', base=base))

        self.assertEqual(missing, [1])
