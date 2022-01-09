import typing as t

from sqlalchemy.orm import DeclarativeMeta, InstrumentedAttribute

from common_amirainvest_com.schemas.schema import Base, Users


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

"""
Needs to get all FKs and init those tables,
Needs to be able to take a faker function in column info and run that to add default data
Needs to take default type and generate blank data for it with required keys,
Needs to take override data for column (via dict)
"""
class Factories:
    def __init__(self, *, session, base: DeclarativeMeta):
        self._session = session
        self._base = base

    def __getitem__(self, item) -> t.Union[t.Callable, t.Coroutine]:
        required_columns = []
        main_class = self._get_sqlalchemy_class(item)

        for name in main_class.__dict__:
            a = main_class.__dict__[name]
            if type(a) == InstrumentedAttribute:
                expression = a.expression
                if len(expression.foreign_keys) > 0:
                    print(expression.foreign_keys)

                if expression.nullable is False:
                    required_columns.append(expression)

                print(expression)
        print(main_class)

    def _get_sqlalchemy_class(self, class_name: str):
        mapper = self._base.registry.mappers
        for mapped_class in mapper:
            if mapped_class.class_.__name__ == class_name:
                return mapped_class.class_
        return None


def main():
    factories = Factories(session="", base=Base)
    a = factories["Bookmarks"]
    print(a)


if __name__ == '__main__':
    main()
