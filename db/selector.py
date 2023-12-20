from .models import ExecutionResponse, Tables, Field, Fields
import typing as tp


class BaseExists:
    template = str()

    def where(self, clause: Field):
        pass


class exists(BaseExists):
    template = 'EXISTS( SELECT 1 FROM {field} WHERE {clause});'


class not_exists(BaseExists):
    template = 'NOT EXISTS( SELECT 1 FROM {field} WHERE {clause});'


class Selector:
    template = "SELECT {fields} FROM {tables} ;"
    clause = "WHERE {clause} ;"

    def __init__(self, cursor, what: tp.Union[str, Fields], from_: Tables, where: tp.Optional[str] = None):
        self.cursor = cursor
        if isinstance(what, (list, tuple, set)):
            what = (field.value if isinstance(field, Field) else field for field in what)
            self.fields = Tables(*what).get_list()
        elif isinstance(what, Field):
            self.fields = [what.value]
        elif isinstance(what, Tables):
            self.fields = what.get_list()
        else:
            print(self.fields)
            raise TypeError("Expected Sequence or Fields, got {type}".format(type=type(what).__name__))

        if isinstance(from_, (list, tuple, set)):
            self.tables = Tables(*from_).get_list()
        elif isinstance(from_, Tables):
            self.tables = from_.get_list()
        else:
            raise TypeError("Expected Sequence or Tables, got {type}".format(type=type(from_).__name__))

        self.where = where
        self.__query = self._form_query()

    def __call__(self, *args, **kwargs):
        return self.fetch(self.cursor)

    def _form_query(self):
        field_row = ",".join(self.fields)
        table_row = ",".join(self.tables)
        query = self.template.format(fields=field_row, tables=table_row)
        return query

    def filter(self, condition):
        self.__query = " ".join((self.__query.replace(";", ""), self.clause.format(clause=condition.value)))
        return self.fetch(self.cursor)

    def fetch(self, cursor) -> ExecutionResponse:
        query = self.__query
        error = None
        result = None

        if query is None:
            return ExecutionResponse(query=query, response=result, error=error)
        print(query)

        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as exc:
            error = str(exc)

        return ExecutionResponse(query=query, response=result, error=error)