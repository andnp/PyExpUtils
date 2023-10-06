import sqlite3
import pandas as pd
import connectorx as cx
from typing import Any, Dict, Iterable, List


def get_tables(cur: sqlite3.Cursor) -> List[str]:
    res = cur.execute("SELECT name FROM sqlite_master")
    return [r[0] for r in res.fetchall()]

def make_table(cur: sqlite3.Cursor, name: str, columns: Iterable[str]):
    cols = ', '.join(map(quote, columns))
    cur.execute(f'CREATE TABLE {name}({cols})')

def maybe_make_table(cur: sqlite3.Cursor, name: str, columns: Iterable[str]):
    tables = get_tables(cur)

    if name not in tables:
        make_table(cur, name, columns)

def get_cols(cur: sqlite3.Cursor, name: str):
    res = cur.execute(f'PRAGMA table_info({name})')
    rows = res.fetchall()

    return [r[1] for r in rows]

def add_cols(cur: sqlite3.Cursor, columns: Iterable[str]):
    columns = map(quote, columns)
    for col in columns:
        cur.execute(f'ALTER TABLE results ADD COLUMN {col}')

def ensure_table_compatible(cur: sqlite3.Cursor, name: str, columns: Iterable[str]):
    columns = set(columns)
    current_cols = set(get_cols(cur, name))
    needed_cols = columns - current_cols

    if needed_cols:
        add_cols(cur, needed_cols)


def query(cur: sqlite3.Cursor, what: str, where: Dict[str, Any]):
    constraints = ' and '.join([f'"{k}"={maybe_quote(v)}' for k, v in where.items()])
    res = cur.execute(f'SELECT {what} FROM results WHERE {constraints}')
    rows = res.fetchall()
    return rows

def constraints_from_lists(cols: Iterable[str], vals: Iterable[Any]):
    c = ' AND '.join(f'"{k}"={maybe_quote(v)}' for k, v in zip(cols, vals))
    return c


def maybe_quote(v: Any):
    if isinstance(v, str):
        return quote(v)
    return v

def quote(s: str):
    return f'"{s}"'


def read_to_df(db_name: str, query: str, part: str | None = None) -> pd.DataFrame:
    # it appears that connectorx has some bugs that cause it to periodically fail.
    # but when it _does_ work, it is 10x faster. So let's try connectorx first, then
    # fall back to the slower pandas for now.
    try:
        n = 4 if part is not None else None
        df: Any = cx.read_sql(f'sqlite://{db_name}', query, partition_on=part, partition_num=n)
        return df
    except BaseException as e:
        print(db_name)
        print(query)
        print(e)
        con = sqlite3.connect(db_name)
        df = pd.read_sql_query(query, con)
        con.close()
        return df
