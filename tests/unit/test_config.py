# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from typing import Any, Optional

import pytest

from i_vis.core import config


class TestConfigMeta:
    @pytest.mark.parametrize(
        "name,vtype,pname",
        [
            ("name1", "foo", "pname1"),
            ("name1", "core", "pname1"),
            ("name1", "pname", None),
        ],
    )
    def test_register_variable_fails(
        self,
        config_meta: config.ConfigMeta,
        name: str,
        vtype: str,
        pname: Optional[str],
    ) -> None:
        with pytest.raises(ValueError):
            config_meta.register_variable(name=name, vtype=vtype, pname=pname)

    @pytest.mark.parametrize(
        "name,required,default",
        [
            ("name1", False, "def1"),
            ("name2", True, None),
        ],
    )
    def test_register_core_variable(
        self,
        config_meta: config.ConfigMeta,
        name: str,
        required: bool,
        default: Optional[Any],
    ) -> None:
        var_name = config_meta.register_core_variable(
            name=name, required=required, default=default
        )
        assert (
            config_meta._name2var[var_name]
            == {
                "pname": None,
                "required": required,
                "default": default,
                "type": "core",
            }
            and not config_meta._pname2vars
        )

    @pytest.mark.parametrize(
        "name,required,pname,default",
        [
            ("name1", False, "pname1", "def1"),
            ("name2", True, "pname2", None),
        ],
    )
    def test_register_plugin_variable(
        self,
        config_meta: config.ConfigMeta,
        name: str,
        required: bool,
        pname: str,
        default: Optional[Any],
    ) -> None:
        var_name = config_meta.register_plugin_variable(
            name=name, required=required, pname=pname, default=default
        )
        assert (
            config_meta._name2var[var_name]
            == {
                "required": required,
                "default": default,
                "pname": pname,
                "type": "plugin",
            }
            and config_meta._pname2vars
        )

    def test_core_vars(self, default_config_meta: config.ConfigMeta) -> None:
        assert default_config_meta.core_vars == (
            "I_VIS_CORE1",
            "I_VIS_CORE2",
            "I_VIS_CORE3",
            "I_VIS_CORE4",
        )

    def test_plugins_vars(self, default_config_meta: config.ConfigMeta) -> None:
        assert default_config_meta.plugin_vars == (
            "I_VIS_PNAME1_VAR1",
            "I_VIS_PNAME1_VAR2",
            "I_VIS_PNAME2_VAR3",
            "I_VIS_PNAME2_VAR4",
        )


@pytest.mark.parametrize(
    "pname,name,expected",
    [
        ("pname1", "name1", "I_VIS_PNAME1_NAME1"),
        ("", "name2", "I_VIS_NAME2"),
    ],
)
def test_variable_name(pname: str, name: str, expected: str) -> None:
    assert config.variable_name(pname=pname, name=name) == expected
