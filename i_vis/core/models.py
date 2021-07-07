"""
User core models and functions.
"""

from typing import Any, Callable, Optional

from flask_login.mixins import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from .db import db
from .ma import ma


def load_user(user_id: int) -> Optional["User"]:
    """Load user.

    Args:
        user_id: User to load.

    Returns:
        User identified with ``user_id``.
    """
    return User.query.get(int(user_id))


def wrap_func(col, func_: Callable) -> Callable:
    """Wrap a function with current context of col.

    Args:
        col:
        func_:

    Returns:
    """

    def wrapped(context) -> Callable:
        return func_(context.current_parameters.get(col.key))

    return wrapped


class User(db.Model, UserMixin):
    """Core user model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    mail = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    last_login_at = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password: str) -> None:
        """Hash and set password."""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password: str) -> bool:
        """Check hashed password."""
        return check_password_hash(self.password, password)

    @classmethod
    def load_by_name(cls, name: str) -> Optional["User"]:
        """Load User by name."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def load_by_mail(cls, mail: str) -> Optional["User"]:
        """Load User by mail."""
        return cls.query.filter_by(mail=mail).first()


class Setting(db.Model):
    """Model for storing settings in DB."""

    __tablename__ = "settings"

    variable = db.Column(db.String(255), primary_key=True)
    value = db.Column(db.PickleType(), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP(), nullable=False, default=func.now(), onupdate=func.now()
    )

    @classmethod
    def get_value(cls, variable: str) -> Optional[Any]:
        setting = db.session.query(cls).get(variable)
        if setting:
            return setting.value
        return None

    @classmethod
    def set_value(cls, variable: str, value: Any) -> "Setting":
        setting = db.session.query(cls).get(variable)
        if setting is None:
            setting = Setting(variable=variable, value=value)
        else:
            setting.value = value
        return setting


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
