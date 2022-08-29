"""Database configuration and access
"""

from flask import Config as FlaskConfig
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import variable_name

#: Use custom convention for naming keys to prevent dialect specific limitations (e.g.: max key length of 64
#: characters).
#: Check `<https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/>`_ for details.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

# extract config from flask
_I_VIS_CONF = variable_name("CONF")
_flask_config = FlaskConfig(__file__)
_flask_config.from_envvar(_I_VIS_CONF)
engine = create_engine(
    url=_flask_config["SQLALCHEMY_DATABASE_URI"],
    max_identifier_length=64,
)


session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base(metadata=metadata)
Base.query = session.query_property()
