import os
import sqlite3
import logging
import pandas as pd
import connectorx as cx
import PyExpUtils.results.sqlite_utils as sqlu

from typing import Iterable

from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.tools import getHeader
from PyExpUtils.results._utils.shared import hash_values

logger = logging.getLogger('PyExpUtils')

def get_values(df: pd.DataFrame | pd.Series, hypers: Iterable[str]):
    hypers = sorted(hypers)

    vals = []
    for h in hypers:
        vals.append(df[h])

    return vals

def v2_to_v3_migration(path: str, exp: ExperimentDescription):
    # it is expensive to do this transformation in-place. Instead, we will build from the backup
    # the backup needs to be readonly to avoid corruption
    os.remove(path)
    back_con = sqlite3.connect('file:' + path + '.backup?mode=ro', uri=True)
    back_cur = back_con.cursor()

    con = sqlite3.connect(path)
    cur = con.cursor()

    sqlu.make_table(cur, 'metadata', ['version'])
    cur.execute('INSERT INTO metadata(version) VALUES("v3")')

    hypers = getHeader(exp)
    hypers = sorted(hypers)
    sqlu.make_table(cur, 'hyperparameters', ['config_id', 'seed'] + hypers)

    hypers_str = ','.join(map(sqlu.quote, hypers))
    df = sqlu.read_to_df(f'{path}.backup', f'SELECT DISTINCT {hypers_str} FROM results')

    metrics = set(df.columns) - {'seed', 'frame', 'config_id'}

    # -------------------------

    cur.execute('ALTER TABLE results ADD COLUMN config_id')

    logger.warning('Updating existing rows')
    for _, row in df.iterrows():
        values = get_values(row, hypers)
        cid = hash_values(values)

        q = ' AND '.join(f'"{k}"={sqlu.maybe_quote(v)}' for k, v in zip(hypers, values))
        cur.execute(f'UPDATE results SET config_id={cid} WHERE {q}')

        cols = ','.join(map(sqlu.quote, ['config_id'] + hypers))
        vals = ','.join(map(str, map(sqlu.maybe_quote, [cid] + values)))
        cur.execute(f'INSERT INTO hyperparameters({cols}) VALUES({vals})')

    cur.connection.commit()

    logger.warning('Creating new table')
    # can't just drop columns in sqlite
    # have to recreate table
    all_cols = sqlu.get_cols(cur, 'results')

    desired_cols = set(all_cols) - set(hypers)
    desired_cols |= { 'config_id' }

    cols = ','.join(map(sqlu.quote, desired_cols))
    cur.execute(f'CREATE TEMPORARY TABLE results_backup({cols})')
    cur.execute(f'INSERT INTO results_backup SELECT {cols} FROM results')
    cur.execute('DROP TABLE results')
    cur.execute(f'CREATE TABLE results({cols})')
    cur.execute(f'INSERT INTO results SELECT {cols} FROM results_backup')
    cur.execute('DROP TABLE results_backup')
    cur.connection.commit()
