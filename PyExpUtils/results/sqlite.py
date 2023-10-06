import os
import sqlite3
import logging
import pandas as pd
import PyExpUtils.results.sqlite_utils as sqlu

from filelock import FileLock
from typing import Iterable, Sequence

from PyExpUtils.collection.Collector import Collector
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.indices import listIndices
from PyExpUtils.results.migrations import maybe_migrate
from PyExpUtils.results.tools import getHeader, getParamValues
from PyExpUtils.results._utils.shared import hash_values

logger = logging.getLogger('PyExpUtils')


# ------------
# -- Saving --
# ------------
def saveCollector(exp: ExperimentDescription, collector: Collector, base: str = './', keys: Iterable[str] | None = None):
    context = exp.buildSaveContext(0, base=base)
    context.ensureExists()

    hypers = getHeader(exp)
    metrics = list(collector.keys())

    res_cols = list(set(['config_id', 'seed', 'frame'] + metrics))
    hyp_cols = list(set(hypers + ['config_id']))

    db_file = context.resolve('results.db')
    with FileLock(db_file + '.lock'):
        if os.path.exists(db_file):
            maybe_migrate(db_file, exp)

        con = sqlite3.connect(db_file, timeout=30)
        cur = con.cursor()

        set_version(cur, 'v2')

        sqlu.maybe_make_table(cur, 'hyperparameters', hyp_cols)
        sqlu.ensure_table_compatible(cur, 'hyperparameters', hyp_cols)

        sqlu.maybe_make_table(cur, 'results', res_cols)
        sqlu.ensure_table_compatible(cur, 'results', res_cols)

        rows = []
        for idx in collector.indices():
            cid = get_cid(cur, hypers, exp, idx)
            seed = exp.getRun(idx)
            frames = collector.get_frames(idx)
            for frame in frames:
                row_dict = frame | {'seed': seed, 'config_id': cid}
                vals = tuple(row_dict.get(k, None) for k in res_cols)
                rows.append(vals)

        cols_str = ', '.join(map(sqlu.quote, res_cols))
        v_inserter = ', '.join('?' * len(res_cols))
        cur.executemany(f'INSERT INTO results({cols_str}) VALUES({v_inserter})', rows)

        con.commit()
        con.close()

# -------------
# -- Loading --
# -------------
def loadResultsOnly(exp: ExperimentDescription, base: str = './', metrics: Sequence[str] | None = None):
    context = exp.buildSaveContext(0, base=base)
    if not context.exists('results.db'):
        return None

    path = context.resolve('results.db')
    maybe_migrate(path, exp)

    con = sqlite3.connect(path)
    cur = con.cursor()

    header = getHeader(exp)
    valid_cids = [
        get_cid(cur, header, exp, i) for i in listIndices(exp)
    ]

    constraints = ','.join(map(str, valid_cids))
    constraints = f'config_id IN ({constraints})'
    if metrics is None:
        df = sqlu.read_to_df(path, f'SELECT * FROM results WHERE {constraints}', part='config_id')
    else:
        cols = set(metrics) | { 'frame', 'seed', 'config_id' }
        col_str = ','.join(map(sqlu.quote, cols))

        non_null = ' AND '.join(f'{m} IS NOT NULL' for m in metrics)
        df = sqlu.read_to_df(path, f'SELECT {col_str} FROM results WHERE {non_null} AND {constraints}', part='config_id')

    return df

def loadHypersOnly(exp: ExperimentDescription, base: str = './') -> pd.DataFrame | None:
    context = exp.buildSaveContext(0, base=base)
    if not context.exists('results.db'):
        return None

    path = context.resolve('results.db')
    config_df = sqlu.read_to_df(path, 'SELECT * FROM hyperparameters')

    return config_df

def loadAllResults(exp: ExperimentDescription, base: str = './', metrics: Sequence[str] | None = None) -> pd.DataFrame | None:
    context = exp.buildSaveContext(0, base=base)
    if not context.exists('results.db'):
        return None

    path = context.resolve('results.db')

    result_df = loadResultsOnly(exp, base, metrics)
    config_df = sqlu.read_to_df(path, 'SELECT * FROM hyperparameters')

    assert result_df is not None
    df = result_df.merge(config_df, on='config_id')

    return df

def detectMissingIndices(exp: ExperimentDescription, runs: int, base: str = './'): # noqa: C901
    context = exp.buildSaveContext(0, base=base)
    nperms = exp.numPermutations()

    header = getHeader(exp)

    # first case: no data
    if not context.exists('results.db'):
        yield from listIndices(exp, runs)
        return

    db_file = context.resolve('results.db')
    maybe_migrate(db_file, exp)
    con = sqlite3.connect(db_file, timeout=30)
    cur = con.cursor()

    tables = sqlu.get_tables(cur)
    if 'results' not in tables:
        yield from listIndices(exp, runs)
        con.close()
        return

    df = sqlu.read_to_df(db_file, 'SELECT DISTINCT config_id,seed FROM results')

    expected_seeds = set(range(runs))
    for idx in listIndices(exp):
        cid = get_cid(cur, header, exp, idx)

        rows = df[df['config_id'] == cid]
        seeds = rows['seed'].unique()
        seeds = set(seeds)

        needed = expected_seeds - seeds
        for seed in needed:
            yield idx + seed * nperms

    con.close()

# ---------------
# -- Utilities --
# ---------------
def get_cid(cur: sqlite3.Cursor, header: Sequence[str], exp: ExperimentDescription, idx: int) -> int:
    values = getParamValues(exp, idx, header)

    # first see if a cid already exists
    if len(header) > 0:
        c = sqlu.constraints_from_lists(header, values)
        res = cur.execute(f'SELECT config_id FROM hyperparameters WHERE {c}')
    else:
        res = cur.execute('SELECT config_id FROM hyperparameters')

    cids = res.fetchall()
    if len(cids) > 0:
        return cids[0][0]

    # otherwise create and store a cid
    cid = hash_values(values)

    if len(header) > 0:
        c_str = ','.join(map(sqlu.maybe_quote, header))
        v_str = ','.join(map(str, map(sqlu.maybe_quote, values)))
        cur.execute(f'INSERT INTO hyperparameters({c_str},config_id) VALUES({v_str},{cid})')
    else:
        cur.execute(f'INSERT INTO hyperparameters(config_id) VALUES({cid})')

    return cid


def set_version(cur: sqlite3.Cursor, version: str):
    sqlu.maybe_make_table(cur, 'metadata', ['version'])

    res = cur.execute('SELECT version FROM metadata')
    v = res.fetchall()

    if len(v) == 0:
        cur.execute(f'INSERT INTO metadata(version) VALUES("{version}")')
    else:
        cur.execute(f'UPDATE metadata SET version="{version}" WHERE version="{v[0]}"')
