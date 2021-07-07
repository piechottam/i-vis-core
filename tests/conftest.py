# pylint: disable=redefined-outer-name

from typing import Generator, Type, TYPE_CHECKING

import pytest
from flask import Flask

from i_vis.core.config import ConfigMeta

if TYPE_CHECKING:
    from i_vis.core.db import db as db_


class FastConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


@pytest.fixture
def fast_config() -> Type[FastConfig]:
    return FastConfig


@pytest.fixture
def config_meta() -> ConfigMeta:
    return ConfigMeta()


@pytest.fixture
def default_config_meta(config_meta: ConfigMeta) -> ConfigMeta:
    # define core vars
    config_meta.register_core_variable(name="core1")
    config_meta.register_core_variable(name="core2", required=True)
    config_meta.register_core_variable(name="core3", default="value3")
    config_meta.register_core_variable(name="core4", required=True, default="value4")

    # define plugin vars
    config_meta.register_plugin_variable(name="var1", pname="pname1")
    config_meta.register_plugin_variable(name="var2", pname="pname1", required=True)
    config_meta.register_plugin_variable(name="var3", pname="pname2", default="value3")
    config_meta.register_plugin_variable(
        name="var4", pname="pname2", required=True, default="value3"
    )

    return config_meta


@pytest.fixture
def dummy_app() -> Generator[Flask, None, None]:
    app = Flask(__name__)
    with app.app_context():
        yield app


@pytest.fixture
def app(fast_config: FastConfig) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.config.from_object(fast_config)

    from i_vis.core.ma import ma
    from i_vis.core.login import login

    with app.app_context():
        ma.init_app(app)
        login.init_app(app)

        yield app


@pytest.fixture
def db(app: Flask) -> Generator["db_", None, None]:
    from i_vis.core.db import db

    db.init_app(app)

    yield db

    db.session.remove()
    db.drop_all()
