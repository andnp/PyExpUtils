import sqlite3
import pandas as pd

from filelock import FileLock
from typing import Any, Iterable, Dict

from PyExpUtils.collection.Collector import Collector
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.indices import listIndices
from PyExpUtils.results.tools import getHeader, getParamsAsDict
from PyExpUtils.utils.dict import flatDict

# TODO: migrate these to a shared location
from PyExpUtils.results.pandas import _subsetDFbyExp

# ------------
# -- Saving --
# ------------
def saveCollector(exp: ExperimentDescription, collector: Collector, base: str = './', keys: Iterable[str] | None = None):
    context = exp.buildSaveContext(0, base=base)
    context.ensureExists()

    header = getHeader(exp)
    metrics = list(collector.keys())

    columns = header + metrics + ['seed', 'frame']

    db_file = context.resolve('results.db')
    if not context.exists('results.db'):
        build_db(db_file, columns)

    con = sqlite3.connect(db_file, timeout=30)
    cur = con.cursor()

    ensure_table_compatible(cur, columns)
    for idx in collector.indices():
        seed = exp.getRun(idx)
        params = getParamsAsDict(exp, idx, header)
        params['seed'] = seed
        frames = collector.get_frames(idx)

        for frame in frames:
            del frame['idx']
            write_row(cur, params | frame)

    con.commit()
    con.close()

# -------------
# -- Loading --
# -------------
def loadAllResults(exp: ExperimentDescription, base: str = './') -> pd.DataFrame | None:
    context = exp.buildSaveContext(0, base=base)
    if not context.exists('results.db'):
        return None

    path = context.resolve('results.db')
    con = sqlite3.connect(path, timeout=30)

    df = pd.read_sql_query('SELECT * FROM results', con)
    con.close()

    return _subsetDFbyExp(df, exp)

def detectMissingIndices(exp: ExperimentDescription, runs: int, base: str = './'): # noqa: C901
    context = exp.buildSaveContext(0, base=base)
    nperms = exp.numPermutations()

    # first case: no data
    if not context.exists('results.db'):
        yield from listIndices(exp, runs)
        return

    db_file = context.resolve('results.db')
    con = sqlite3.connect(db_file, timeout=30)
    cur = con.cursor()

    expected_seeds = set(range(runs))
    for idx in listIndices(exp):
        params = exp.getPermutation(idx)['metaParameters']
        flat_params = flatDict(params)

        rows = query(cur, 'seed', flat_params)
        seeds = set(r[0] for r in rows)

        needed = expected_seeds - seeds
        for seed in needed:
            yield idx + seed * nperms


# ---------------
# -- Utilities --
# ---------------
def build_db(db_file: str, columns: Iterable[str]):
    with FileLock(db_file + '.lock'):
        con = sqlite3.connect(db_file, timeout=30)
        cur = con.cursor()

        # make sure the table exists and has the needed columns
        maybe_make_table(cur, columns)
        con.commit()
        con.close()

def get_tables(cur: sqlite3.Cursor):
    res = cur.execute("SELECT name FROM sqlite_master")
    return res.fetchall()

def make_table(cur: sqlite3.Cursor, columns: Iterable[str]):
    cols = ', '.join(map(_quote, columns))
    cur.execute(f'CREATE TABLE results({cols})')

def maybe_make_table(cur: sqlite3.Cursor, columns: Iterable[str]):
    tables = get_tables(cur)

    if not any('results' in t[0] for t in tables):
        make_table(cur, columns)

def get_cols(cur: sqlite3.Cursor):
    res = cur.execute('PRAGMA table_info(results)')
    rows = res.fetchall()

    return [r[1] for r in rows]

def add_cols(cur: sqlite3.Cursor, columns: Iterable[str]):
    columns = map(_quote, columns)
    for col in columns:
        cur.execute(f'ALTER TABLE results ADD COLUMN {col}')

def ensure_table_compatible(cur: sqlite3.Cursor, columns: Iterable[str]):
    columns = set(columns)
    current_cols = set(get_cols(cur))
    needed_cols = columns - current_cols

    if needed_cols:
        add_cols(cur, needed_cols)

def write_row(cur: sqlite3.Cursor, data: Dict[str, Any]):
    columns, values = zip(*data.items())
    header = ', '.join(map(_quote, columns))
    vals = ', '.join('?' * len(data))
    cur.execute(f'INSERT INTO results({header}) VALUES({vals})', values)

def query(cur: sqlite3.Cursor, what: str, where: Dict[str, Any]):
    constraints = ' and '.join([f'"{k}"={v}' for k, v in where.items()])
    res = cur.execute(f'SELECT {what} FROM results WHERE {constraints}')
    rows = res.fetchall()
    return rows


def _quote(s: str):
    return f'"{s}"'
