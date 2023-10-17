import psycopg2 as psycopg
from psycopg2.pool import SimpleConnectionPool
from db.cfg_reader import get_database
import typing as tp
from functools import partial


__all__ = "Connector"


class BaseConnectionClass:
    pools = dict()

    def __init__(self, database=None, host=None, port=None, user=None, password=""):
        self.new_state(ClosedConnectionClass)
        self.db_name = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def new_state(self, state):
        state: tp.Union[ClosedConnectionClass, OpenConnectionClass]
        self.__class__ = state

    def conn_open(self):
        raise NotImplementedError

    def __conn_close(self):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class ClosedConnectionClass(BaseConnectionClass):

    def __enter__(self):
        self.conn_open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.new_state(ClosedConnectionClass)
        self.__conn_close()
        print(self)

    def conn_open(self):
        self.new_state(OpenConnectionClass)
        if self.db_name not in self.pools:

        dbase = get_database(self.db_name)
        self.connection = psycopg.connect(
            host=self.host if self.host else dbase.host,
            user=self.user if self.user else dbase.user,
            port=self.port if self.port else dbase.port,
            dbname=self.db_name,
            password=self.password
        )
        self.cursor = self.connection.cursor()

    def __conn_close(self):
        self.connection.close()


class OpenConnectionClass(BaseConnectionClass):

    def conn_open(self):
        raise RuntimeError("Already open!")

    def __conn_close(self):
        raise RuntimeError("Already closed!")

    def __enter__(self):
        raise RuntimeError("Already open!")

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError("Already closed!")

    def execute(self, command):
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def insert(self, *, into: str, fields: tp.Sequence[str] = (), values: tp.Sequence[tp.Any]) -> bool:
        scheme = """INSERT INTO {into}{fields} VALUES {values};"""
        try:
            fields = '(' + ",".join(fields) + ')' if fields else ""
        except TypeError as err:
            print("Expected Sequence[str]", err)
            return False

        query = scheme.format(into=into, fields=fields, values=values)
        print(query)
        resp = self.cursor.execute(query)
        self.connection.commit()
        return resp


class Connector:
    __password = None

    @staticmethod
    def set_global_password(password):
        if not isinstance(password, str):
            password = str(password)
        Connector.__password = password

    @staticmethod
    def delete_gloabl_password():
        Connector.__password = None

    @staticmethod
    def get(*, dbase, host=None, port=None, user=None, password=""):
        if Connector.__password is not None:
            password = Connector.__password
        return partial(BaseConnectionClass, database=dbase, password=password, port=port, host=host, user=user)