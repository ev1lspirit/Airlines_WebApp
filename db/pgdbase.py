from psycopg2.pool import SimpleConnectionPool
from psycopg2.errors import lookup as pg_errorlookup
import psycopg2.errorcodes as pg_error
from db.cfg_reader import get_database
import typing as tp
import logging
from functools import partial
from dataclasses import dataclass


logging.basicConfig(level=logging.DEBUG)
__all__ = "Connector", "ExecutionResponse"


@dataclass
class ExecutionResponse:
    query: tp.Optional[str]
    response: tp.Optional[str]
    error: tp.Optional[dict[str, str]]


class BaseConnectionClass:
    pools: dict[str, SimpleConnectionPool] = dict()
    logger = logging.getLogger(name='BaseConnectionClass')

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

    def conn_close(self):
        raise NotImplementedError

    def __enter__(self):
        raise RuntimeError("Can't use context manager with {self.__class__.__name__}".format(self=self))

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError


class ClosedConnectionClass(BaseConnectionClass):

    def __enter__(self):
        self.logger.debug("Connection to {name} has been opened!".format(name=self.db_name))
        self.conn_open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Connection to {name} has been closed!".format(name=self.db_name))
        self.conn_close()

    def conn_open(self):
        self.new_state(OpenConnectionClass)
        dbase = get_database(self.db_name)
        if self.db_name not in self.pools:
            self.logger.debug("Connection pool for {name} is created!".format(name=self.db_name))
            self.pools[self.db_name] = SimpleConnectionPool(
                    minconn=3, maxconn=5,
                    host=self.host if self.host else dbase.host,
                    user=self.user if self.user else dbase.user,
                    port=self.port if self.port else dbase.port,
                    dbname=self.db_name,
                    password=self.password
                )

        self.connection = self.pools[self.db_name].getconn()
        self.logger.debug("Cursor for {name} is opened!".format(name=self.db_name))
        self.cursor = self.connection.cursor()

    def conn_close(self):
        raise RuntimeError("Already closed!")


class OpenConnectionClass(BaseConnectionClass):

    def conn_open(self):
        raise RuntimeError("Already open!")

    def conn_close(self):
        self.new_state(ClosedConnectionClass)
        self.logger.debug("Cursor for {name} is closed!".format(name=self.db_name))
        self.cursor.close()

    def execute(self, command):
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def insert(self, *, into: str, fields: tp.Sequence[str] = (), values: tp.Sequence[tp.Any]) -> ExecutionResponse:
        scheme = """INSERT INTO {into}{fields} VALUES {values};"""
        try:
            fields = '(' + ",".join(fields) + ')' if fields else ""
        except TypeError as err:
            print("Expected Sequence[str]", err)
            return ExecutionResponse(response=None, query=None, error={"error": "Expected Sequence[str] {err}".format(err=err)})

        query = scheme.format(into=into, fields=fields, values=values)
        print(query)
        error = True

        try:
            resp = self.cursor.execute(query)
            self.connection.commit()
            self.logger.debug("{name}: Inserted into {into}{fields} values {values}".format(
                name=self.db_name, into=into, fields=fields, values=values))
            error = False

        except pg_errorlookup(pg_error.UNIQUE_VIOLATION) as err:
            resp = {"error_code": 100, "cause": str(err)}
            self.logger.error("{err} :raised while executing {query}\n".format(err=str(err), query=query))

        except pg_errorlookup(pg_error.NOT_NULL_VIOLATION) as err:
            resp = {"error_code": 101, "cause": str(err)}

        except pg_errorlookup(pg_error.FOREIGN_KEY_VIOLATION) as err:
            resp = {"error_code": 102, "cause": str(err)}

        return ExecutionResponse(query=query,
                                 response=resp if not error else None,
                                 error=resp if error else None)


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
    def get(*, dbase, host=None, port=None, user=None, password="") -> partial[BaseConnectionClass]:
        if Connector.__password is not None:
            password = Connector.__password
        return partial(BaseConnectionClass, database=dbase, password=password, port=port, host=host, user=user)

    @staticmethod
    def close_pools():
        for _, pool in BaseConnectionClass.pools:
            pool.closeall()