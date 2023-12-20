from dataclasses import dataclass
from itertools import chain
import typing as tp

__all__ = "Alias", "Table", "Field", "Fields", "CrossJoin", "LeftJoin", "FullOuterJoin", "RightJoin", \
          "Join", "ExecutionResponse"


class Tables:
    def __init__(self, *table_names):
        self.table_names = set(field.name if isinstance(field, Table) else str(field) for field in table_names)
        self.aliased = tuple("".join((field.name, " AS ", field.alias)) for field in table_names if
                             isinstance(field, Alias) and field.alias != field.name)

    def get_list(self):
        return list(chain(self.table_names, self.aliased))


@dataclass(frozen=True)
class Alias:
    name: str
    alias: str

    def __getattr__(self, item):
        return Field(value=".".join((self.alias, str(item))))


class Fields:
    def __init__(self, *field_names):
        self.fields = list(field for field in field_names if isinstance(field, str))

    def get_list(self):
        return self.fields


class Field:
    __slots__ = "value", "_dep"

    def __init__(self, *, value, _dep=()):
        self.value = str(value)
        self._dep = _dep

    def __eq__(self, other: str):
        return Field(value="{value} = '{other}'".format(value=str(self.value), other=other))

    def __ge__(self, other):
        return Field(value="{value} >= '{other}'".format(value=str(self.value), other=other))

    def __le__(self, other):
        return Field(value="{value} <= '{other}'".format(value=str(self.value), other=other))

    def __gt__(self, other):
        return Field(value="{value} > '{other}'".format(value=str(self.value), other=other))

    def __lt__(self, other):
        return Field(value="{value} < '{other}'".format(value=str(self.value), other=other))

    def __ne__(self, other):
        return Field(value="{value} <> '{other}'".format(value=str(self.value), other=other))

    def __and__(self, other):
        return Field(value="({value} and {other})".format(value=str(self.value), other=other.value))

    def __or__(self, other):
        return Field(value="({value} or {other})".format(value=str(self.value), other=other.value))


@dataclass(frozen=True)
class Table:
    name: str

    def join(self, other):
        return Join(first_table=self, other_table=other)

    def left_join(self, other):
        return LeftJoin(first_table=self, other_table=other)

    def right_join(self, other):
        return RightJoin(first_table=self, other_table=other)

    def full_join(self, other):
        return FullOuterJoin(first_table=self, other_table=other)

    def cross_join(self, other):
        return CrossJoin(first_table=self, other_table=other)

    def __getattr__(self, item):
        return Field(value='.'.join((self.name, str(item))), _dep=self.name)


class BaseJoin:
    template: str = None

    def __init__(self, first_table, other_table):
        if not isinstance(other_table, Table) or not isinstance(first_table, Table):
            raise TypeError('Expected Table, got {type} insetad'.format(type=type(other_table).__name__))
        self.other_table = other_table
        self.first_table = first_table

    def __call__(self, *args, **kwargs) -> Table:
        return Table(self.template.format(table=self.first_table.name,
                                          table2=self.other_table.name,
                                          predicate="true"))

    def on(self, predicate) -> Table:
        if not isinstance(predicate, Field):
            raise TypeError('Expected Table, got {type} insetad'.format(type=type(predicate).__name__))

        return Table(self.template.format(
            table=self.first_table.name,
            table2=self.other_table.name,
            predicate=predicate))


class Join(BaseJoin):
    template = "{table} JOIN {table2} ON {predicate};"


class LeftJoin(BaseJoin):
    template = "{table} LEFT JOIN {table2} ON {predicate};"


class RightJoin(BaseJoin):
    template = "{table} RIGHT JOIN {table2} ON {predicate};"


class FullOuterJoin(BaseJoin):
    template = "{table} FULL OUTER JOIN {table2} ON {predicate};"


class CrossJoin(BaseJoin):
    template = "{table} CROSS JOIN {table2} ON {predicate};"


@dataclass
class ExecutionResponse:
    query: tp.Optional[str]
    response: tp.Optional[str]
    error: tp.Optional[dict[str, str]]


