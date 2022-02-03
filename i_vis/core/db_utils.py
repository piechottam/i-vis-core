"""
Utility functions for database(s) """

import sys
import warnings
from logging import getLogger
from os.path import basename
from typing import Any, Sequence, Type

from inflection import underscore
from sqlalchemy import inspect
from sqlalchemy.sql import func

from flask_sqlalchemy.model import DefaultMeta

from .db import db

logger = getLogger()


PREFIX = "i_vis"
def i_vis_col(col: str) -> str:
    return "_".join([PREFIX, col])


def i_vis_cols(cols: Sequence[str]) -> Sequence[str]:
    return tuple(i_vis_col(col) for col in cols)


def fname2tname(fname: str) -> str:
    """Transform fname to tname.

    Create a database friendly table name for a given filename.

    Args:
        fname: Filename to transform.

    Returns:
        Transformed table name.

    """
    # remove path
    fname = basename(fname)
    # remove suffix
    pos = fname.find(".")
    if pos >= 0:
        fname = fname[0:pos]
    tname = underscore(fname)
    return tname


def get_table(tname: str) -> DefaultMeta:
    """Get model for table name.

    Args:
        tname: Name of the table to retrieve model for.

    Returns:
        Model for table

    Raises:
        KeyError if ``tname`` is not found
    """
    for model in db.Model.__subclasses__():
        if hasattr(model, "__tablename__") and model.__tablename__ == tname:
            return model

    raise KeyError(tname)


def column_names(mixin: Type[Any]) -> Sequence[str]:
    """Get column names for a mixin.

    The column name is either:
    * the name within the class mixin <name> = db.Column([...]) or
    * the name within var = db.Column([...], name=<name>)

    Args:
        mixin: The mixin class to inspect for columns.

    Returns:
        Sequence of column names contained in ``mixin``.
    """
    # catch warnings otherwise sqlalchemy will complain
    # that a columns in a mixin are not mapped yet to table
    with warnings.catch_warnings():
        if not sys.warnoptions:
            warnings.simplefilter("ignore")
        return tuple(
            var.name if var.name else name
            for name, var in vars(mixin).items()
            if isinstance(var, db.Column)
        )


def row_count(tname: str) -> int:
    """Get row count for table.

    Args:
        tname: The table name to retrieve row count.

    Returns:
        The number of rows for a table.
    """

    table = get_table(tname)
    # TODO TEST primary_key = model.__mapper__.primary_key[0].name
    pks = tuple(pk for pk in table.__table__.primary_key.columns)
    return int(db.session.query(func.count(*pks)).scalar())
    # apparently slower: return model.query.count()


def get_column_name(column: db.Column) -> str:
    with warnings.catch_warnings():
        return str(getattr(column, "name"))


def missing_tables() -> Sequence[str]:
    obj = inspect(db.engine)
    return [
        table.name
        for table in db.metadata.sorted_tables
        if not obj.dialect.has_table(db.engine.connect(), table.name)
    ]


def tables_exist() -> bool:
    return not missing_tables()
