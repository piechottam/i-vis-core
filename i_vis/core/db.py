from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

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
db = SQLAlchemy(
    metadata=metadata,
    engine_options={"max_identifier_length": 64},
    session_options={"expire_on_commit": False},
)
