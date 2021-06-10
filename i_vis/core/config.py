"""
Manages config info in i_vis
"""

from typing import Any, Mapping, MutableMapping, Optional, Sequence
import os

from flask import current_app


class Default:
    DEBUG = False
    TESTING = False


class Testing:
    DEBUG = True
    TESTING = True


class MissingConfig(Exception):
    pass


class MissingVariable(Exception):
    def __init__(self, variable: str):
        Exception.__init__(self)
        self.variable = variable

    def __str__(self) -> str:
        return f"Missing variable: {self.variable}"


_NAME2VAR: MutableMapping[str, Any] = {}
_PNAME2VAR: MutableMapping[str, Any] = {}


def get_name2variable() -> Mapping[str, Any]:
    return dict(_NAME2VAR)


def get_pname2variable() -> Mapping[str, Any]:
    return dict(_PNAME2VAR)


def _register_variable(
    pname: str,
    name: str,
    vtype: str,
    required: bool = False,
    default: Optional[str] = None,
) -> str:
    var = variable_name(pname=pname, name=name)
    meta = {"type": vtype, "required": required, "pname": pname}
    if default is not None:
        meta["default"] = default
    _NAME2VAR[var] = meta
    _PNAME2VAR.setdefault(pname, {})[var] = meta
    return var


def variable_name(name: str, pname: str = "") -> str:
    if pname:
        return f"I_VIS_{pname}_{name}".upper()
    return f"I_VIS_{name}".upper()


def register_core_variable(
    name: str, required: bool = True, default: Optional[Any] = None
) -> str:
    return _register_variable("", name, "core", required, default)


def register_plugin_variable(
    pname: str, name: str, required: bool = True, default: Optional[Any] = None
) -> str:
    return _register_variable(pname, name, "plugin", required, default)


def set_pname_defaults(pname: str) -> None:
    for var_name, meta in _PNAME2VAR.get(pname, {}).items():
        if "default" in meta and var_name not in current_app.config:
            current_app.config[var_name] = meta["default"]


def set_defaults() -> None:
    for var_name, meta in _NAME2VAR.items():
        if "default" in meta and var_name not in current_app.config:
            current_app.config[var_name] = meta["default"]


def check_pname_config(pname: str) -> None:
    for var_name, meta in _PNAME2VAR.get(pname, {}).items():
        if meta["required"] and var_name not in current_app.config:
            raise MissingVariable(var_name)


def check_config(pnames: Optional[Sequence[str]] = None) -> None:
    for var_name, meta in _NAME2VAR.items():
        pname = meta["pname"]
        if (
            meta["required"]
            and var_name not in current_app.config
            and (not pnames or pname in pnames)
        ):
            raise MissingVariable(var_name)


def add_secret_key(config: MutableMapping[str, Any], cookie_name: Optional[str] = None, secret_key: Optional[str] = None) -> None:
    config.update(
        SECRET_KEY=secret_key if secret_key is not None else os.urandom(24),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_NAME=cookie_name,
        WTF_CSRF_TIME_LIMIT=None,
    )
