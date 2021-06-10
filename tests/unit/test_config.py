# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pytest

from i_vis.core import config
from i_vis.core.config import add_secret_key


@pytest.fixture
def empty_config():
    config._NAME2VAR.clear()
    config._PNAME2VAR.clear()


@pytest.fixture
# pylint: disable=unused-argument
def dummy_config(empty_config):
    config.register_core_variable("core_var1", required=True)
    config.register_plugin_variable("pname1", "var1", required=True)


@pytest.mark.usefixtures("empty_config")
class TestGetRegisteredVariables:
    def test_empty(self):
        assert not config.get_name2variable()

    def test_not_empty(self):
        config.register_core_variable("core_var1", required=True)
        config.register_plugin_variable("pname1", "var1", required=True)
        assert config.get_name2variable()


@pytest.mark.usefixtures("dummy_config")
class TestGetValue:
    def test_get_value(self):
        assert not config.get_name2variable()["CORE_VAR1"]
        assert not config.get_name2variable()["PNAME1_VAR1"]

    def test_get_value_raises(self):
        with pytest.raises(config.MissingVariable):
            _ = dummy_config.get_value("TEST")


def test_register_variable():
    pass
    # tested via wrapper:
    # * test_register_core_variable
    # * test_register_plugin_variable


@pytest.mark.parametrize(
    "pname,name,expected",
    [
        ("pname1", "name1", "I_VIS_PNAME1_NAME1"),
        ("", "name2", "I_VIS_NAME2"),
    ],
)
def test_variable_name(pname: str, name: str, expected: str):
    assert config.variable_name(pname=pname, name=name) == expected


def test_register_core_variable():
    config.register_core_variable(name="CORE")
    core_var = "I_VIS_CORE"
    assert core_var in config.get_name2variable()
    assert config.get_name2variable()[core_var]["type"] == "core"
    assert "default" not in config.get_name2variable()[core_var]


def test_register_plugin_variable():
    config.register_plugin_variable(pname="pname1", name="var1")
    plugin_var = "I_VIS_PNAME1_VAR1"
    assert plugin_var in config.get_name2variable()
    assert config.get_name2variable()[plugin_var]["type"] == "plugin"
    assert "default" not in config.get_name2variable()[plugin_var]


class TestSetDefaults:
    pass


class TestCheckConfig:
    def test_nothing_required(self):
        assert False

    def test_core_var_required(self):
        assert False

    def test_plugin_var_required(self):
        assert False

    def test_specific_pnames(self):
        assert False


def test_add_secret_key():
    test_config = {}
    add_secret_key(test_config, "cookie_name")
    assert test_config["SECRET_KEY"] and len(test_config["SECRET_KEY"]) == 24
    assert test_config["SESSION_COOKIE_SECURE"]
    assert test_config["SESSION_COOKIE_NAME"] == "cookie_name"
    assert not test_config["WTF_CSRF_TIME_LIMIT"]
