# pylint: disable=redefined-outer-name

from typing import TYPE_CHECKING
import pytest

from i_vis.core import models

if TYPE_CHECKING:
    from i_vis.core.db import db as db_


@pytest.fixture
def mini_user() -> models.User:
    user = models.User(name="test_name1", mail="test_mail1")
    user.set_password("test_password1")
    return user


@pytest.fixture
# pylint: disable=unused-argument
def created_user(db: "db_", mini_user: models.User) -> models.User:
    db.create_all()
    db.session.add(mini_user)
    db.session.commit()
    return mini_user


# pylint: disable=unused-argument
def test_user_load(db: "db_", mini_user: models.User) -> None:
    db.create_all()
    assert models.load_user(1) is None
    db.session.add(mini_user)
    db.session.commit()
    assert models.load_user(mini_user.id) == mini_user


class TestUser:
    def test_create(self, created_user: models.User) -> None:
        assert created_user.id == 1
        assert created_user.name == "test_name1"
        assert created_user.mail == "test_mail1"
        assert (
            created_user.password is not None
            and created_user.password != "test_password1"
        )
        assert created_user.created_at is not None
        assert created_user.updated_at is not None
        assert created_user.created_at == created_user.updated_at
        assert created_user.last_login_at is None
        assert not created_user.is_admin

    def test_unique_name_fails(self, db: "db_", created_user: models.User) -> None:
        with pytest.raises(Exception):
            user = models.User(
                name="test_name1", mail="test_mail2", password="test_password2"
            )
            db.session.add(user)
            db.session.commit()

    def test_unique_mail_fails(self, db: "db_", created_user: models.User) -> None:
        with pytest.raises(Exception):
            user = models.User(
                name="test_name2", mail="test_mail1", password="test_password2"
            )
            db.session.add(user)
            db.session.commit()

    def test_check_password(self, created_user: models.User) -> None:
        assert created_user.check_password("test_password1")

    def test_check_password_fails(self, created_user: models.User) -> None:
        assert not created_user.check_password("wrong")

    def test_load_by_name(self, created_user: models.User) -> None:
        assert models.User.load_by_name("test_name1") == created_user

    def test_load_by_name_fails(self, created_user: models.User) -> None:
        assert models.User.load_by_name("test_name2") is None

    def test_load_by_mail(self, created_user: models.User) -> None:
        assert models.User.load_by_mail("test_mail1") == created_user

    def test_load_by_mail_fails(self, created_user: models.User) -> None:
        assert models.User.load_by_name("test_mail2") is None


@pytest.fixture
# pylint: disable=unused-argument
def created_setting(db: "db_") -> models.Setting:
    db.create_all()
    setting = models.Setting(variable="var1", value=("val1", "val2"))
    db.session.add(setting)
    db.session.commit()
    return setting


class TestSetting:
    def test_create(self, created_setting: models.Setting) -> None:
        assert created_setting.variable == "var1"
        assert created_setting.value == ("val1", "val2")
        assert created_setting.updated_at is not None

    def test_get_value(self, created_setting: models.Setting) -> None:
        assert models.Setting.get_value("var1") == created_setting.value

    def test_get_value_fails(self, created_setting: models.Setting) -> None:
        assert models.Setting.get_value("var2") is None

    def test_set_value(self, created_setting: models.Setting) -> None:
        assert models.Setting.get_value("var1") == created_setting.value
        models.Setting.set_value("var1", "value1")
        assert models.Setting.get_value("var1") == "value1"
