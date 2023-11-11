from psycopg2.pool import SimpleConnectionPool
from db.cfg_reader import get_database
import typing as tp
import logging
from functools import wraps, partial

from .selector import Selector
from .models import Fields, Field, Tables, ExecutionResponse

logging.basicConfig(level=logging.DEBUG)


__all__ = "Connector",


def pooled(outer_cls=None, minconn=3, maxconn=5):
    if outer_cls is None:
        return partial(pooled, minconn=minconn, maxconn=maxconn)

    @wraps(outer_cls.__new__)
    def __new__(cls, *args, **kwargs):
        db_name = kwargs.get("database")

        if not hasattr(cls, "pools"):
            setattr(cls, "pools", dict())

        _, instance = cls.pools.get(db_name, (None, None))

        if instance is None:
            dbase = get_database(db_name)
            instance = super(cls, cls).__new__(cls)
            host = kwargs.pop("host")
            user = kwargs.pop("user")
            port = kwargs.pop("port")
            print(kwargs)
            cls.pools[db_name] = (SimpleConnectionPool(minconn=3, maxconn=5,
                host=host if host else dbase.host,
                user=user if user else dbase.user,
                port=port if port else dbase.port,
                dbname=db_name,
                password=kwargs.pop("password")), instance)

        return instance

    outer_cls.__new__ = __new__
    return outer_cls


# insert into airplanemodel values ('737', 'Boeing', 4500, 11000);


@pooled(maxconn=7, minconn=2)
class BaseConnectionClass:
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
        self.current_pool = None

    def new_state(self, state):
        state: tp.Union[ClosedConnectionClass, OpenConnectionClass]
        self.__class__ = state

    def conn_open(self):
        raise NotImplementedError

    def conn_close(self):
        raise NotImplementedError

    def __enter__(self):
        raise RuntimeError("Can't use context manager with {self.__class__.__name__}".format(self=self))


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
        self.current_pool, _ = self.pools[self.db_name]
        self.connection = self.current_pool.getconn()
        self.logger.debug("Cursor for {name} is opened!".format(name=self.db_name))
        self.cursor = self.connection.cursor()
        print(self.cursor)

    def conn_close(self):
        raise RuntimeError("Already closed!")


class OpenConnectionClass(BaseConnectionClass):

    def __init__(self, database=None, host=None, port=None, user=None, password=""):
        super().__init__(database=database, host=host, port=port, user=user, password=password)

    def conn_open(self):
        raise RuntimeError("Already open!")

    def conn_close(self):
        self.current_pool.putconn(self.connection)
        self.logger.debug("Cursor for {name} is closed!".format(name=self.db_name))
        self.cursor.close()
        self.new_state(ClosedConnectionClass)

    def create(self, command) -> ExecutionResponse:
        message = False
        error = None
        try:
            self.cursor.execute(command)
            self.connection.commit()
            message = True
        except Exception as exc:
            error = str(exc)
            self.logger.error(f"Error during exuctuing script: {error}")
        return ExecutionResponse(query=command, response=message, error=error)

    def select(self, what: Fields, from_: Tables) -> Selector:
        if not isinstance(what, (list, tuple, set, Field, Fields)) or not isinstance(from_, (list, tuple, set,Tables)):
            raise TypeError('Expected default types as input Fields, Tables, got {what_type}, {from_type} '
                            ''.format(what_type=type(what).__name__, from_type=type(from_).__name__))

        return Selector(cursor=self.cursor, what=what, from_=from_)

    def _select(self, *, query):
        error = None
        response = None
        try:
            self.cursor.execute(query)
        except Exception as exc:
            error = str(exc)

        return ExecutionResponse(query=query, response=response, error=error)

    def insert(self, *, into: str, fields: tp.Sequence[str] = (), values: tp.Sequence[tp.Any]) -> ExecutionResponse:
        scheme = """INSERT INTO {into}{fields} VALUES {values};"""
        try:
            fields = '(' + ",".join(fields) + ')' if fields else ""
        except TypeError as err:
            print("Expected Sequence[str]", err)
            return ExecutionResponse(response=None, query=None, error={"error": "Expected Sequence[str] {err}".format(err=err)})

        query = scheme.format(into=into, fields=fields, values=values)
        error = True
        error_map = {"error_code": 500, "cause": None}
        resp = None

        try:
            resp = self.cursor.execute(query)
            self.connection.commit()
            self.logger.debug("{name}: Inserted into {into}{fields} values {values}".format(
                name=self.db_name, into=into, fields=fields, values=values))
            error = False

        except Exception as err:
            error_map["cause"] = str(err)

        if error is True:
            self.logger.error("Failed query: {query} \nException: {err}\n".format(err=error_map["cause"], query=query))

        return ExecutionResponse(query=query,
                                 response=resp if not error else None,
                                 error=error_map if error else None)


class Connector:
    __password = None

    @staticmethod
    def set_global_password(password):
        if not isinstance(password, str):
            password = str(password)
        Connector.__password = password

    @staticmethod
    def delete_global_password():
        Connector.__password = None

    @staticmethod
    def get(*, dbase, host=None, port=None, user=None, password=None) -> BaseConnectionClass:
        if password is None and Connector.__password is not None:
            password = Connector.__password
        return BaseConnectionClass(database=dbase, password=password, port=port, host=host, user=user)


if __name__ == "__main__":
    pass