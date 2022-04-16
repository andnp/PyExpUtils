from __future__ import annotations
import os
import glob
import importlib
import pandas as pd
from typing import Any, Callable, Dict, List, Optional, TypeVar, overload
from PyExpUtils.utils.dict import flatKeys, get
from PyExpUtils.utils.NestedDict import NestedDict
from PyExpUtils.utils.permute import set_at_path
from PyExpUtils.models.ExperimentDescription import loadExperiment
from PyExpUtils.results.backends.pandas import loadResults
from PyExpUtils.results.results import ResultList

RList = TypeVar('RList', bound=ResultList)
class ResultCollection(NestedDict[str, pd.DataFrame]):
    def __init__(self):
        super().__init__(depth=2)

        self._data: Dict[str, Dict[str, pd.DataFrame]] = {}

    def apply(self, f: Callable[[pd.DataFrame], pd.DataFrame | None]):
        for key in self:
            out = f(self[key])
            if out is not None:
                self[key] = out

        return self

    @classmethod
    def fromExperiments(cls, file: str, path: Optional[str] = None) -> ResultCollection:
        exp_files = findExperiments('{domain}', path)

        out = cls()
        for domain in exp_files:
            paths = exp_files[domain]
            for p in paths:
                alg = p.split('/')[-1].replace('.json', '')

                exp = loadExperiment(p)
                df = loadResults(exp, file)

                out[domain, alg] = df

        return out

    @classmethod
    def fromResults(cls, env_alg_result: NestedDict[str, RList]) -> ResultCollection:
        out = cls()

        for domain, alg in env_alg_result:
            results = env_alg_result[domain, alg]
            results = list(results)
            exp = results[0].exp
            idx = results[0].idx

            params = exp.getPermutation(idx)['metaParameters']
            keys = flatKeys(params)
            header = sorted(keys)

            # avoid having to construct a list by appending
            def _rowBuilder():
                for r in results:
                    pvalues = [get(r.params, k) for k in header]
                    for run, data in enumerate(r.load()):
                        if not isinstance(data, list):
                            data = [data]

                        yield pvalues + [run] + list(data)

            rows = list(_rowBuilder())

            out[domain, alg] = pd.DataFrame(rows, columns=header + ['run', 'data'])

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
