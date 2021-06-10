from typing import Any, Optional

from flask_login.mixins import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from . import ma


def load_user(user_id: int) -> Optional["User"]:
    return User.query.get(int(user_id))


def wrap_func(col, func):
    def wrapped(context):
        return func(context.current_parameters.get(col.key))

    return wrapped


class User(db.Model, UserMixin):  # type: ignore
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

    def set_password(self, password) -> None:
        """Create hashed password"""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password) -> bool:
        """Check hashed password"""
        return check_password_hash(self.password, password)

    @classmethod
    def load_by_name(cls, name: str) -> Optional["User"]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def load_by_mail(cls, mail: str) -> Optional["User"]:
        return cls.query.filter_by(mail=mail).first()


class Setting(db.Model):  # type: ignore
    __tablename__ = "settings"

    variable = db.Column(db.String(255), primary_key=True)
    value = db.Column(db.PickleType(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(), nullable=False, onupdate=func.now())

    @classmethod
    # pylint: disable=no-self-use
    def get_value(self, variable: str) -> Optional[Any]:
        return self.query.get(variable)

    @classmethod
    def set_value(cls, variable: str, value: Any) -> "Setting":
        setting = cls.query.get(variable)
        if setting is None:
            setting = Setting(variable=variable, value=value)
        else:
            setting.value = value
        return setting


class UserSchema(ma.SQLAlchemyAutoSchema):  # type: ignore
    class Meta:
        model = User
