import os
import shutil
import unittest
import pandas as pd
from typing import List
from PyExpUtils.utils.NestedDict import NestedDict
from PyExpUtils.results.backends.backend import BaseResult
from PyExpUtils.results.Collection import ResultCollection
from PyExpUtils.models.ExperimentDescription import ExperimentDescription

exps = NestedDict[str, ExperimentDescription](2)
for domain in ['da', 'db', 'dc']:
    for alg in ['a', 'b', 'c']:
        exps[domain, alg] = ExperimentDescription({
            'alg': alg,
            'env': domain,
            'metaParameters': {
                'alpha': [1.0, 0.5, 0.25],
                'ratio': [1.0, 2.0, 4.0, 8.0],
            },
        })

class TestResult(BaseResult):
    def _load(self):
        return [self.idx + i for i in range(3)]

class TestCollection(unittest.TestCase):
    files: List[str] = []

    def getBase(self):
        return '.tests/test_collection'

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

    def test_fromResults(self):
        results = exps.map(lambda exp: [TestResult('./', exp, i) for i in range(12)])

        collection = ResultCollection.fromResults(results)

        keys = list(collection.keys())
        self.assertEqual(keys, ['da', 'db', 'dc'])

        subkeys = list(collection[keys[0]])
        self.assertEqual(subkeys, ['a', 'b', 'c'])

        sub = collection['da', 'a']
        self.assertIsInstance(sub, pd.DataFrame)

        runs = 3
        params = 12
        self.assertEqual(len(sub), runs * params)
