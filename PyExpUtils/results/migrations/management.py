import shutil
import sqlite3
import logging
import PyExpUtils.results.sqlite_utils as sqlu

from glob import glob

from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.migrations.v2 import v1_to_v2_migration

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

    cur.close()
    con.close()

    # TODO: we can make this smarter by registering a->b migrators, then finding
    # the shortest migration path between any two versions.
    # For now, with so few versions, we take the lazy path.
    if version == 'v1':
        logger.warning('Migrating from v1->v2 of data version')
        make_backup(db_name)

        try:
            v1_to_v2_migration(db_name, exp)
        except Exception as e:
            restore_backup(db_name)
            raise e

    elif version == 'v2':
        ...

    else:
        raise Exception('Cannot figure out how to migrate to latest data version')


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
