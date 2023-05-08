from __future__ import annotations
import os
import glob
import importlib
import pandas as pd
from typing import Any, Callable, Dict, List, Optional, Type, overload
from PyExpUtils.utils.NestedDict import NestedDict
from PyExpUtils.utils.permute import set_at_path
from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.pandas import loadResults

class ResultCollection(NestedDict[str, pd.DataFrame]):
    def __init__(self, Model: Optional[Type[ExperimentDescription]] = None):
        super().__init__(depth=2)

        self._data: Dict[str, Dict[str, pd.DataFrame]] = {}
        self._Model = Model

    def apply(self, f: Callable[[pd.DataFrame], pd.DataFrame | None]):
        for key in self:
            item = self[key]
            if item is None:
                continue

            out = f(item)

            if out is not None:
                self[key] = out

        return self

    def map(self, f: Callable[[pd.DataFrame], pd.DataFrame]):
        out = ResultCollection(self._Model)

        for key in self:
            out[key] = f(self[key])

        return out

    @classmethod
    def fromExperiments(cls, file: str, path: Optional[str] = None, Model: Optional[Type[ExperimentDescription]] = None) -> ResultCollection:
        exp_files = findExperiments('{domain}', path)

        out = cls(Model=Model)
        for domain in exp_files:
            paths = exp_files[domain]
            for p in paths:
                alg = p.split('/')[-1].replace('.json', '')

                exp = loadExperiment(p, Model)
                df = loadResults(exp, file)

                if df is not None:
                    out[domain, alg] = df

        return out

@overload
def findExperiments(key: str, path: Optional[str] = None) -> Dict[str, Any]: ...
@overload
def findExperiments() -> List[str]: ...

def findExperiments(key: Optional[str] = None, path: Optional[str] = None):
    if path is None:
        main_file = importlib.import_module('__main__').__file__
        assert main_file is not None
        path = os.path.dirname(main_file)

    files = glob.glob(f'{path}/**/*.json', recursive=True)

    if key is None:
        return files

    out: Dict[str, Any] = {}
    kparts = key.split('/')
    for i, fname in enumerate(files):
        # remove the common experiment path leading up to here
        end = fname.replace(path, '')
        # if there is a nested structure, we might have a leading '/' now,
        # so for consistency, remove that
        if end.startswith('/'): end = end[1:]

        fparts = end.split('/')

        out_key = ''
        for kpart, fpart in zip(kparts, fparts):
            wrapped = kpart.startswith('{') and kpart.endswith('}')

            if not wrapped:
                continue

            if fpart.endswith('.json'):
                fpart = fpart.replace('.json', '')

            if out_key == '':
                out_key = fpart

            else:
                out_key += f'.{fpart}'

        out_key += f'.[{i}]'
        set_at_path(out, out_key, fname)

    return out
