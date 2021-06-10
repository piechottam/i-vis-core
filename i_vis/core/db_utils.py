from logging import getLogger
from os.path import basename
from typing import Sequence, Type
import sys
import warnings

from inflection import underscore
from pandas import DataFrame
from sqlalchemy import inspect
from sqlalchemy.sql import func
from sqlalchemy.sql.selectable import TableClause
from tqdm import tqdm

import pandas as pd

from . import db


logger = getLogger()


def read_db(tname: str, **kwargs) -> DataFrame:
    rows = pd.read_sql(f"SELECT COUNT(*) as rows FROM {tname}", kwargs["con"]).at[
        0, "rows"
    ]
    gen = pd.read_sql_table(table_name=tname, **kwargs)

    df = DataFrame()
    for chunk in tqdm(
        gen, desc="Retrieving rows", total=rows, unit=" rows", unit_scale=True
    ):
        df = df.append(chunk, ignore_index=True)
    return df


def fname2tname(fname: str) -> str:
    # remove path
    tmp_fname = basename(fname)
    # remove suffix
    i = tmp_fname.find(".")
    if i >= 0:
        tmp_fname = tmp_fname[0:i]
    tname = underscore(tmp_fname)
    return tname


def get_model(tname: str) -> TableClause:
    for model in db.Model.__subclasses__():
        if model.__tablename__ == tname:
            return model
    raise KeyError(tname)


# def get_table_columns(tbl: TableClause) -> Sequence[db.Column]:  # type: ignore
#    return tbl.__table__.c


def column_names(mixin: Type) -> Sequence[str]:
    cols = []
    with warnings.catch_warnings():
        if not sys.warnoptions:
            warnings.simplefilter("ignore")
        for _, var in vars(mixin).items():
            if isinstance(var, db.Column):
                cols.append(var.name)
    return cols


def row_count(tname: str) -> int:
    model = get_model(tname)
    pk = model.__mapper__.primary_key[0].name
    return int(db.session.query(func.count(getattr(model, pk))).scalar())
    # apparently slower: return model.query.count()


def get_column_name(db_column: db.Column) -> str:
    with warnings.catch_warnings():
        return str(getattr(db_column, "name"))

def missing_tables() -> Sequence[str]:
    insp = inspect(db.engine)
    return [
            table.name
            for table in db.meta_data.sorted_tables
            if not insp.dialect.has_table(db.engine.connect(), table.name)
    ]


def tables_exist() -> bool:
    return not missing_tables()