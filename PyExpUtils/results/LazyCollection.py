from __future__ import annotations
import os
import glob
import importlib
import pandas as pd

from typing import Any, Generic, Sequence, Tuple, Type, TypeVar

from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.sqlite import loadAllResults, loadHypersOnly, loadResultsOnly
from PyExpUtils.results.tools import getHeader


Exp = TypeVar('Exp', bound=ExperimentDescription)
CExp = TypeVar('CExp', bound=ExperimentDescription)


class LazyResult(Generic[Exp]):
    def __init__(self, exp: Exp, path: str, metrics: Sequence[str] | None):
        self.metrics = metrics
        self.exp = exp
        self.path = path

    def load(self) -> pd.DataFrame | None:
        return loadAllResults(self.exp, metrics=self.metrics)

    def load_metrics(self) -> pd.DataFrame | None:
        return loadResultsOnly(self.exp, metrics=self.metrics)

    def load_hypers(self) -> pd.DataFrame | None:
        return loadHypersOnly(self.exp)


class GroupbyResult(LazyResult):
    def __init__(self, exp: Any, path: str, sub_path: str, metrics: Sequence[str] | None):
        super().__init__(exp, path, metrics)
        self.sub_path = sub_path

class LazyResultCollection(Generic[Exp]):
    def __init__(self, path: str | None = None, metrics: Sequence[str] | None = None, Model: Type[Exp] | None = None):
        self._Model = Model or ExperimentDescription
        self._path = path
        self._metrics = metrics

        if self._path is None:
            main_file = importlib.import_module('__main__').__file__
            assert main_file is not None
            self._path = os.path.dirname(main_file)

        project = os.getcwd()
        paths = glob.glob(f'{self._path}/**/*.json', recursive=True)
        paths = [ p.replace(f'{project}/', '') for p in paths ]
        self._paths = paths

    def result(self, path: str) -> LazyResult[Exp]:
        exp: Any = loadExperiment(path, self._Model)

        return LazyResult[Exp](
            exp=exp,
            path=path,
            metrics=self._metrics,
        )

    def groupby_directory(self, level: int):
        uniques = set([
            p.split('/')[level] for p in self._paths
        ])

        for group in uniques:
            group_paths = [p for p in self._paths if p.split('/')[level] == group]
            results = map(self.result, group_paths)

            yield group, [_sub_path(r, level) for r in results]

    def get_hyperparameter_columns(self):
        hypers = set[str]()

        for path in self._paths:
            exp = loadExperiment(path, Model=self._Model)
            sub = getHeader(exp)
            hypers |= set(sub)

        return list(sorted(hypers))

    def __iter__(self):
        return map(self.result, self._paths)

    def __getitem__(self, key: str | Tuple[str, ...]) -> LazyResult[Exp]:
        if isinstance(key, str):
            key = (key, )

        matches = []
        for k in self._paths:
            parts = k.split('/')
            parts[-1] = parts[-1].replace('.json', '')
            if all(any(query == part for part in parts) for query in key):
                matches.append(k)

        if len(matches) == 0:
            raise KeyError('Could not find an experiment matching query')

        if len(matches) > 1:
            raise KeyError(f'Found too many experiments for query: {len(matches)}')

        return self.result(matches[0])


def _sub_path(r: LazyResult, level: int):
    sub_parts = r.path.split('/')[level + 1:]
    sub = '/'.join(sub_parts)
    sub = sub.replace('.json', '')
    return GroupbyResult(
        exp=r.exp,
        path=r.path,
        sub_path=sub,
        metrics=r.metrics,
    )
