import configparser
from dataclasses import dataclass
import os

__all__ = "DBConfigurationClass", "get_database"

path = os.path.dirname(os.path.realpath(__file__))
configdir = '/'.join((path, 'dbconfig.ini'))

config = configparser.ConfigParser()
config.read(configdir)


@dataclass
class DBConfigurationClass:
    host: str
    port: int
    user: str
    db: str


class DatabaseNotFound(Exception):
    pass


def get_database(db_name) -> DBConfigurationClass:
    if db_name not in config.sections():
        raise DatabaseNotFound("Can't find database: {name}".format(name=db_name))

    db_field = config[db_name]
    return DBConfigurationClass(
        host=db_field.get("host"),
        port=db_field.getint("port"),
        user=db_field.get("user"),
        db=db_name
    )
