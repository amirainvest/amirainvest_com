import typing as t
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from common_amirainvest_com.schemas.schema import Base

# def test(global_session, factories):
#     user = factories.Users(interests_value=True)
#     factories.Users()
#     # 2 users
#
#
# def test_2(global_session, factories):
#     bookmarks = factories.Bookmarks()
#     user_id = bookmarks.user_id
#     post_id = bookmarks.post_id
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session


"""
Needs to be able to take a faker function in column info and run that to add default data
Needs to take override data for column (via dict),
TODO Why is posts id not incrementing.
"""

column_type_default = {
    sa.String: str,
    sa.Integer: int,
    sa.Boolean: bool,
    sa.DECIMAL: Decimal,
}


class Factories:
    def __init__(self, *, session: AsyncSession, base: DeclarativeMeta):
        self._session: AsyncSession = session
        self._base = base
        self._table_data = {}

    # def __getitem__(self, item) -> t.Union[t.Callable, t.Coroutine]:
    async def gen(self, item):
        main_table: sa.Table = self._get_table(item)

        tables = self._get_fk_tables(main_table.foreign_keys)
        tables[main_table] = None

        for table in tables:
            self._table_data[table] = {
                "declarative_meta": self._table_to_declarative_meta(table),
                "pushed_instance": None,
            }

        for table in self._table_data:
            await self._create_row(table)

        return_data = {}
        for table, values in self._table_data.items():
            return_data[table.name] = values["pushed_instance"]
        return return_data

    async def _create_row(self, table: sa.Table):
        row_dict = {}
        column: sa.Column
        for column in table.columns:
            key = column.key
            if column.info.get("factory") is not None:
                factory = column.info["factory"]
                generator = factory.get("generator")
                if generator is not None:
                    generator_function = generator[0]
                    generator_function_args = generator[1]
                    if generator_function_args is not None:
                        value = generator_function(generator_function_args)
                    else:
                        value = generator_function()
                else:
                    value = column.info["default"]
            elif len(column.foreign_keys) != 0:
                if len(column.foreign_keys) > 1:
                    raise ValueError("More than one FK")
                fk = column.foreign_keys.pop()
                fk_table = fk.column.table
                fk_key = fk.column.key

                fk_pushed_table = self._table_data[fk_table]["pushed_instance"]
                value = getattr(fk_pushed_table, fk_key)
            elif (
                column.nullable is False
                and column.default is None
                and column.server_default is None
                and column.autoincrement is not True
            ):
                if type(column.type) == sa.Enum:
                    value = column.type.enums[0]
                else:
                    value = column_type_default[type(column.type)]()
            else:
                continue

            row_dict[key] = value

        dm_table: sa.orm.DeclarativeMeta = self._table_data[table]["declarative_meta"]
        self._table_data[table]["pushed_instance"] = dm_table(**row_dict)
        self._session.add(self._table_data[table]["pushed_instance"])
        await self._session.flush()
        await self._session.refresh(self._table_data[table]["pushed_instance"])

    def _table_to_declarative_meta(self, table: sa.Table) -> sa.orm.DeclarativeMeta:
        mappers = self._base.registry.mappers
        mapper: sa.orm.Mapper
        for mapper in mappers:
            if mapper.mapped_table == table:
                return mapper.class_
        raise ValueError("Reverse mapping didn't work")

    def _get_fk_tables(self, fks: t.Set[sa.ForeignKey], fk_tables=None) -> t.Dict[sa.Table, None]:
        if fk_tables is None:
            fk_tables = {}
        for fk in fks:
            fk_table = fk.column.table
            if len(fk_table.foreign_keys) != 0:
                self._get_fk_tables(fk_table.foreign_keys, fk_tables)
            fk_tables[fk_table] = None
        return fk_tables

    def _get_table(self, table_class_name: str) -> sa.Table:
        mappers = self._base.registry.mappers
        mapper: sa.orm.Mapper
        for mapper in mappers:
            if mapper.class_.__name__ == table_class_name:
                return mapper.mapped_table
            if mapper.mapped_table.name == table_class_name:
                return mapper.mapped_table

        raise ValueError(f"No table class with name {table_class_name}")


@Session
async def run(session):
    factories = Factories(session=session, base=Base)
    a = await factories.gen("bookmarks")
    print(a)


async def main():
    await run()


if __name__ == "__main__":
    run_async_function_synchronously(main)
