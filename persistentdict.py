import os
from contextlib import contextmanager
import sqlite3
import pickle
import yaml

from const import SQLITE_SOURCE_FILE


@contextmanager
def get_cursor(db_wrapper):
    connection = db_wrapper.connection
    cursor = connection.cursor()
    yield cursor
    cursor.close()
    connection.commit()


class PersistentDict(object):

    descriptor = None
    connection = None
    sqls = dict()

    def __init__(self, connection_str):
        if os.path.isabs(connection_str):
            filepath = connection_str
        else:
            filepath = os.path.join(os.getcwd(), connection_str)
        self.descriptor = filepath
        self.connection = sqlite3.connect(filepath)
        with open(SQLITE_SOURCE_FILE, 'r') as sqlite_source:
            self.sqls = yaml.safe_load(sqlite_source)
        self._validate_sqls()
        self._ensure_schema()

    def __del__(self):
        if (self.connection):
            self.connection.close()

    def _validate_sqls(self):
        assert isinstance(self.sqls, dict), f"Invalid source yaml, dict expected in '{SQLITE_SOURCE_FILE}'"
        for sql_key, sql_obj in self.sqls.items():
            assert isinstance(sql_obj, dict), f"Invalid yaml structure, dict expected for key '{sql_key}'"
            assert 'type' in sql_obj, f"Source type missing for key '{sql_key}"
            assert isinstance(sql_obj['type'], str), f"Invalid type, string expected for key '{sql_key}'"
            sql_obj['type'] = sql_obj['type'].strip().lower()
            assert sql_obj['type'] in ('script', 'create', 'select', 'insert', 'update', 'delete'), f"Invalid type for key '{sql_key}'"
            assert 'sql' in sql_obj, f"Source code missing for key '{sql_key}"
            assert isinstance(sql_obj['sql'], str), f"Invalid yaml structure, source string expected for '{sql_key}:sql']"

    def _execute(self, sql_key, sql_args = ()):
        assert sql_key in self.sqls, f"Missing code from source file '{SQLITE_SOURCE_FILE}': '{sql_key}'"
        sql_obj = self.sqls[sql_key]
        with get_cursor(self) as cursor:
            cursor.execute(sql_obj['sql'], sql_args)
            if sql_obj['type'] == 'select':
                return cursor.fetchall()
            elif sql_obj['type'] in ('insert', 'update'):
                return cursor.lastrowid

    def _ensure_schema(self):
        self._execute('create schema')

    def __len__(self):
        return self._execute('get length')[0][0]

    def __getitem__(self, key):
        rs = self._execute('get value', (pickle.dumps(key), ))
        if len(rs) == 0:
            raise KeyError(f"'{key}'")
        else:
            return pickle.loads(rs[0][0])

    def __setitem__(self, key, value):
        self._execute('set item', (pickle.dumps(key), pickle.dumps(value)))

    def __delitem__(self, key):
        self._execute('delete item', (pickle.dumps(key), ))

    def __contains__(self, key):
        return self._execute('contains key', (pickle.dumps(key), ))[0][0] >= 1

    def __iter__(self):
        rs = self._execute('get all keys')
        return iter(pickle.loads(r[0]) for r in rs)

    def __str__(self):
        base_str = f'Dict-like persistent key-value store'
        if hasattr(self, 'descriptor'):
            return f'{base_str} at {self.descriptor}'
        else:
            return base_str

    def keys(self):
        return self.__iter__()

    def values(self):
        rs = self._execute('get all values')
        return iter(pickle.loads(r[0]) for r in rs)

    def items(self):
        rs = self._execute('get all items')
        return iter((pickle.loads(r[0]), pickle.loads(r[1])) for r in rs)

    def get(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            return default

    def copy(self):
        return {key:value for key, value in self.items()}

    def clear(self):
        self._execute('purge data')

    def replace(self, a_dict):
        if not isinstance(a_dict, dict):
            raise ValueError(f"Dict expected")
        self.clear()
        for key, value in a_dict.items():
            self[key] = value

    def update(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                self[key] = value
        else:
            # less efficient fallback to the builtin
            self.replace(self.copy().update(data))

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError(f"pop expected at most 2 arguments, got {len(args) + 1}")
        elif len(args) == 1:
            value = self.get(key, args[0])
        else:
            value = self[key]
        del self[key]
        return value

    def popitem(self):
        rs = self._execute('get one item')
        if len(rs) == 0:
            raise KeyError(f"popitem(): dictionary is empty")
        key = pickle.loads(rs[0][0])
        del self[key]
        return (key, pickle.loads(rs[0][1]))

    def setdefault(self, key, default = None):
        if key not in self:
            self[key] = default
            return default
        else:
            return self[key]
