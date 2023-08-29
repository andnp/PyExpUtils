from __future__ import annotations
import os
import glob
import importlib
import dataclasses
import pandas as pd

from typing import Callable, Dict, Generic, Optional, Sequence, Type, TypeVar

from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.sqlite import loadAllResults
from PyExpUtils.results.tools import getHeader


Exp = TypeVar('Exp', bound=ExperimentDescription)


@dataclasses.dataclass
class Result(Generic[Exp]):
    exp: Exp
    df: pd.DataFrame
    path: str

class ResultCollection:
    def __init__(self, Model: Optional[Type[Exp]] = None):
        self._data: Dict[str, Result] = {}
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

    @classmethod
    def fromExperiments(cls, path: Optional[str] = None, Model: Optional[Type[Exp]] = None) -> ResultCollection:
        paths = findExperiments(path)

        out = cls(Model=Model)
        for p in paths:
            exp = loadExperiment(p, Model)
            df = loadAllResults(exp)

            if df is not None:
                out._data[p] = Result(
                    exp=exp,
                    df=df,
                    path=p,
                )

        return out


def findExperiments(path: Optional[str] = None):
    if path is None:
        main_file = importlib.import_module('__main__').__file__
        assert main_file is not None
        path = os.path.dirname(main_file)

    paths = glob.glob(f'{path}/**/*.json', recursive=True)

    project = os.getcwd()
    return [ p.replace(f'{project}/', '') for p in paths ]
