from db import Connector
import os

path = os.path.dirname(os.path.realpath(__file__))
dbdir = '/'.join((path, 'database.sql'))

WebAirlinesDB = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])
print(WebAirlinesDB)


def setup():
    with open(dbdir, 'r', encoding='utf-8') as sql_script:
        with WebAirlinesDB as conn:
            for statement in sql_script.read().split(";"):
                statement = "".join((statement.strip(), ";"))
                try:
                    conn.create(statement)
                except Exception as exc:
                    print(str(exc))


if __name__ == "__main__":
     setup()
