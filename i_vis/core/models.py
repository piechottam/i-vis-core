"""
User core models and functions.
"""

from typing import Any, cast, Callable, Optional, Union
from secrets import token_urlsafe

from flask_login.mixins import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean, PickleType, TIMESTAMP
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.sql import func
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from werkzeug.security import generate_password_hash, check_password_hash

from .constants import API_TOKEN_LENGTH
from .db import Base, session


def load_user(user_id: int) -> Optional["User"]:
    """Load user.

    Args:
        user_id: User to load.

    Returns:
        User identified with ``user_id``.
    """
    user = User.query.get(int(user_id))
    if user:
        return cast(User, user)

    return None


#  replace any with column type
def wrap_func(
    col: Union[str, Any], func_: Callable[[Any], Any]
) -> Callable[[Any], Any]:
    """Wrap a function with current context of col.

    Args:
        col:
        func_:

    Returns:
    """
    if not isinstance(col, str):
        col = col.key

    def wrapped(context: DefaultExecutionContext) -> Any:
        assert context.current_parameters is not None
        return func_(context.current_parameters.get(col))

    return wrapped


def create_token() -> str:
    for _ in range(1, 5):
        token = token_urlsafe(API_TOKEN_LENGTH)
        user = User.load_by_token(token)
        if not user:
            return token[:API_TOKEN_LENGTH]
    raise Exception()


class User(Base, UserMixin):
    """Core user model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    mail = Column(String(120), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    last_login_at = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    token = Column(
        String(API_TOKEN_LENGTH),
        nullable=False,
        unique=True,
        index=True,
        default=create_token,
    )

    def set_password(self, password: str) -> None:
        """Hash and set password."""

        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password: str) -> bool:
        """Check hashed password."""

        assert self.password is not None
        return check_password_hash(self.password, password)

    @classmethod
    def load_by_name(cls, name: str) -> Optional["User"]:
        """Load User by name."""
        user = cls.query.filter_by(name=name).first()
        if user:
            return cast(User, user)

        return None

    @classmethod
    def load_by_mail(cls, mail: str) -> Optional["User"]:
        """Load User by mail."""
        user = cls.query.filter_by(mail=mail).first()
        if user:
            return cast(User, user)

        return None

    @classmethod
    def load_by_token(cls, token: str) -> Optional["User"]:
        user = cls.query.filter_by(token=token).first()
        if not user:
            return None
        return cast("User", user)

    __mapper_args = {
        "always_refresh": True,
    }


class Setting(Base):
    """Model for storing settings in DB."""

    __tablename__ = "settings"

    variable = Column(String(255), primary_key=True)
    value = Column(PickleType(), nullable=False)
    updated_at = Column(
        TIMESTAMP(), nullable=False, default=func.now(), onupdate=func.now()
    )

    @classmethod
    def get_value(cls, variable: str) -> Optional[Any]:
        setting = session.query(cls).get(variable)
        if setting:
            return setting.value
        return None

    @classmethod
    def set_value(cls, variable: str, value: Any) -> "Setting":
        setting = session.query(cls).get(variable)
        if setting is None:
            setting = Setting(variable=variable, value=value)
        else:
            setting.value = value
        return cast(Setting, setting)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
