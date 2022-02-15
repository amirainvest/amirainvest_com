from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Bundle, Query


def query_to_string(query: Query) -> str:
    # TODO do ::uuid/datetime if the string is uuid/timestamp in the params
    dialect = postgresql.base.PGDialect()
    # https://docs.sqlalchemy.org/en/20/faq/sqlexpressions.html?highlight=render_postcompile#rendering-postcompile-parameters-as-bound-parameters
    compiler = postgresql.base.PGCompiler(dialect, query, compile_kwargs={"render_postcompile": True})

    return str(compiler) % compiler.params


class DictBundle(Bundle):
    def create_row_processor(self, query, procs, labels):
        """Override create_row_processor to return values as dictionaries"""

        def proc(row):
            return dict(zip(labels, (proc(row) for proc in procs)))

        return proc
