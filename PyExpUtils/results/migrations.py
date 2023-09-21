import shutil
import sqlite3
import logging
import pandas as pd
import connectorx as cx
import PyExpUtils.results.sqlite_utils as sqlu

from glob import glob
from typing import Iterable

from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.tools import getHeader
from PyExpUtils.results._utils.shared import hash_values

logger = logging.getLogger('PyExpUtils')

def detect_version(cur: sqlite3.Cursor) -> str:
    tables = sqlu.get_tables(cur)

    if 'metadata' not in tables:
        return 'v1'

    res = cur.execute('SELECT version FROM metadata')
    version = res.fetchone()

    if version is None:
        return 'v1'

    return version[0]

def maybe_migrate(db_name: str, exp: ExperimentDescription):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    version = detect_version(cur)

    if version == 'v1':
        logger.warning('Migrating from v1->v2 of data version')
        make_backup(db_name)

        try:
            v1_to_v2_migration(db_name, cur, exp)
        except Exception as e:
            restore_backup(db_name)
            raise e

    elif version == 'v2':
        ...

    else:
        raise Exception('Cannot figure out how to migrate to latest data version')

    cur.close()
    con.close()

def restore_backup(db_name: str):
    backups = glob(db_name + '.*.backup')
    latest = backups[-1]

    logger.warning(f'Attempting to restore {db_name} from backup {latest}')
    shutil.copyfile(latest, db_name)

def make_backup(db_name: str):
    backups = glob(db_name + '.*.backup')
    num = len(backups)
    dst = f'{db_name}.{num}.backup'

    logger.warning(f'Making a backup of {db_name} at {dst}')
    shutil.copyfile(db_name, dst)

def get_values(df: pd.DataFrame | pd.Series, hypers: Iterable[str]):
    hypers = sorted(hypers)

    vals = []
    for h in hypers:
        vals.append(df[h])

    return vals

def v1_to_v2_migration(path: str, cur: sqlite3.Cursor, exp: ExperimentDescription):
    sqlu.make_table(cur, 'metadata', ['version'])
    cur.execute('INSERT INTO metadata(version) VALUES("v2")')

    hypers = getHeader(exp)
    hypers = sorted(hypers)
    sqlu.make_table(cur, 'hyperparameters', ['config_id'] + hypers)

    hypers_str = ','.join(map(sqlu.quote, hypers))
    df = cx.read_sql(f'sqlite://{path}', f'SELECT DISTINCT {hypers_str} FROM results')

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
