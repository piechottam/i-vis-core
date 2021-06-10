from flask_login.login_manager import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from .__version__ import __MAJOR__, __MINOR__, __PATCH__, __SUFFIX__
from .version import Default as DefaultVersion

VERSION = DefaultVersion(
    major=__MAJOR__, minor=__MINOR__, patch=__PATCH__, suffix=__SUFFIX__
)

# max 64

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(
    metadata=metadata,
    engine_options={"max_identifier_length": 64},
    session_options={"expire_on_commit": False},
)
login = LoginManager()
ma = Marshmallow()
