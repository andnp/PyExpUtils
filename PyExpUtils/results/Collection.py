from __future__ import annotations
import os
import glob
import importlib
import dataclasses
import pandas as pd

from typing import Any, Callable, Dict, Generic, Optional, Sequence, Tuple, Type, TypeVar
from multiprocessing.dummy import Pool

from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.sqlite import loadAllResults
from PyExpUtils.results.tools import getHeader


Exp = TypeVar('Exp', bound=ExperimentDescription)
CExp = TypeVar('CExp', bound=ExperimentDescription)


@dataclasses.dataclass
class Result(Generic[Exp]):
    exp: Exp
    df: pd.DataFrame
    path: str

class ResultCollection(Generic[Exp]):
    def __init__(self, Model: Optional[Type[Exp]] = None):
        self._data: Dict[str, Result[Exp]] = {}
        self._Model = Model

    def apply(self, f: Callable[[pd.DataFrame], pd.DataFrame | None]):
        for item in self._data.values():
            out = f(item.df)

            if out is not None:
                item.df = out

        return self

    def map(self, f: Callable[[pd.DataFrame], pd.DataFrame]):
        out = ResultCollection(self._Model)

        for key, item in self._data.items():
            out._data[key] = Result(
                exp=item.exp,
                df=f(item.df),
                path=item.path,
            )

        return out

    def combine(self, folder_columns: Sequence[str | None], file_col: str | None):
        out: pd.DataFrame | None = None
        for path in self._data.keys():
            parts = path.split('/')
            assert len(parts) == len(folder_columns) + 1

            df = self._data[path].df

            for fcol, part in zip(folder_columns, parts):
                if fcol is None: continue

                df[fcol] = part

            if file_col is not None:
                df[file_col] = parts[-1].replace('.json', '')

            if out is None:
                out = df
            else:
                out = pd.concat((out, df), axis=0, ignore_index=True)

        if out is not None:
            out.reset_index(drop=True, inplace=True)

        return out

    def get_hyperparameter_columns(self):
        hypers = set[str]()

        for res in self._data.values():
            sub = getHeader(res.exp)
            hypers |= set(sub)

        return list(sorted(hypers))

    def get_any_exp(self):
        k = next(iter(self._data))
        return self._data[k].exp

    def __iter__(self):
        return iter(self._data.values())

    def __getitem__(self, key: str | Tuple[str, ...]) -> Result:
        if isinstance(key, str):
            return self._data[key]

        matches = []
        for k in self._data:
            parts = k.split('/')
            parts[-1] = parts[-1].replace('.json', '')
            if all(any(query == part for part in parts) for query in key):
                matches.append(self._data[k])

        if len(matches) == 0:
            raise KeyError('Could not find an experiment matching query')

        if len(matches) > 1:
            raise KeyError(f'Found too many experiments for query: {len(matches)}')

        return matches[0]

    @classmethod
    def fromExperiments(cls, metrics: Sequence[str] | None = None, path: Optional[str] = None, Model: Type[CExp] = ExperimentDescription) -> ResultCollection[CExp]:
        pool = Pool()
        paths = findExperiments(path)
        out: Any = cls(Model=Model)

        def load_path(p: str):
            exp = loadExperiment(p, Model)
            df = loadAllResults(exp, metrics=metrics)

            if df is not None:
                out._data[p] = Result(
                    exp=exp,
                    df=df,
                    path=p,
                )

        pool.map(load_path, paths)

        return out


def findExperiments(path: Optional[str] = None):
    if path is None:
        main_file = importlib.import_module('__main__').__file__
        assert main_file is not None
        path = os.path.dirname(main_file)

    paths = glob.glob(f'{path}/**/*.json', recursive=True)

    project = os.getcwd()
    return [ p.replace(f'{project}/', '') for p in paths ]
