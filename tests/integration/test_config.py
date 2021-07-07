from contextlib import nullcontext as does_not_raise
from typing import Any, Optional

import pytest
from flask import Flask

from i_vis.core import config


class TestConfigMeta:

    # pylint: disable=unused-argument
    def test_set_defaults(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_defaults()

        assert default_config_meta.core_vars == (
            "I_VIS_CORE1",
            "I_VIS_CORE2",
            "I_VIS_CORE3",
            "I_VIS_CORE4",
        ) and default_config_meta.plugin_vars == (
            "I_VIS_PNAME1_VAR1",
            "I_VIS_PNAME1_VAR2",
            "I_VIS_PNAME2_VAR3",
            "I_VIS_PNAME2_VAR4",
        )

    # pylint: disable=unused-argument
    def test_set_core_defaults(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_core_defaults()

        assert default_config_meta.core_vars == (
            "I_VIS_CORE1",
            "I_VIS_CORE2",
            "I_VIS_CORE3",
            "I_VIS_CORE4",
        )

    # pylint: disable=unused-argument
    def test_set_pnames_defaults(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_plugin_defaults()

        assert default_config_meta.plugin_vars == (
            "I_VIS_PNAME1_VAR1",
            "I_VIS_PNAME1_VAR2",
            "I_VIS_PNAME2_VAR3",
            "I_VIS_PNAME2_VAR4",
        )

    def test_check_config(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_defaults()
        dummy_app.config["I_VIS_CORE2"] = "value2"
        dummy_app.config["I_VIS_PNAME1_VAR2"] = "value2"

        default_config_meta.check_config()
        assert True

    def test_check_core_config(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_defaults()
        dummy_app.config["I_VIS_CORE2"] = "value2"

        default_config_meta.check_core_config()
        assert True

    def test_check_plugin_config(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_defaults()
        dummy_app.config["I_VIS_PNAME1_VAR2"] = "value2"

        default_config_meta.check_plugin_config()
        assert True

    def test_check_config_core_fails(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_defaults()

        with pytest.raises(config.MissingVariable) as excinfo:
            default_config_meta.check_core_config()
        assert excinfo.value.variable == "I_VIS_CORE2"

    def test_check_config_plugin_fails(
        self, dummy_app: Flask, default_config_meta: config.ConfigMeta
    ) -> None:
        default_config_meta.set_defaults()

        with pytest.raises(config.MissingVariable) as excinfo:
            default_config_meta.check_plugin_config()
        assert excinfo.value.variable == "I_VIS_PNAME1_VAR2"


@pytest.mark.parametrize(
    "vtype,required,value,expectation",
    [
        ("core", True, "value", does_not_raise()),
        ("core", True, None, pytest.raises(config.MissingVariable)),
        ("core", False, "value", does_not_raise()),
        ("core", False, None, does_not_raise()),
        ("plugin", True, "value", does_not_raise()),
        ("plugin", True, None, pytest.raises(config.MissingVariable)),
        ("plugin", False, "value", does_not_raise()),
        ("plugin", False, None, does_not_raise()),
    ],
)
# pylint: disable=unused-argument
def test_check_meta(
    dummy_app: Flask,
    config_meta: config.ConfigMeta,
    vtype: str,
    required: bool,
    value: Optional[Any],
    expectation: Any,
) -> None:
    kwargs = {"name": "var", "vtype": vtype, "required": required, "default": value}
    if vtype == "plugin":
        kwargs["pname"] = "pname"
    var_name = config_meta.register_variable(**kwargs)
    dummy_app.config[var_name] = value

    with expectation:
        # pylint: disable=protected-access
        config._check_meta(var_name=var_name, meta=config_meta.name2var[var_name])
