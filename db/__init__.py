from .pgdbase import Connector

'''class PostgreConnector:

    def __init__(self, database=None, host=None, port=None, user=None, password=""):
        self.db_name = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def __enter__(self):
        dbase = get_database(self.db_name)
        self.connection = psycopg.connect(
            host=self.host if self.host else dbase.host,
            user=self.user if self.user else dbase.user,
            port=self.port if self.port else dbase.port,
            dbname=self.db_name,
            password=self.password,
            autocommit=True
        )
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()'''