"""Manages config and meta info.
"""

from typing import Any, Mapping, MutableMapping, Optional, Sequence
from flask import Flask, current_app, Config

_flask_config = Config(root_path="")


class Default:
    DEBUG = False
    TESTING = False


class Testing(Default):
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


class ConfigMeta:
    """Container for config meta."""

    def __init__(self) -> None:
        self._name2var: MutableMapping[str, Any] = {}
        self._pname2vars: MutableMapping[str, MutableMapping[str, Any]] = {}

    def clear(self) -> None:
        self._name2var.clear()
        self._pname2vars.clear()

    # pylint: disable=too-many-arguments
    def register_variable(
            self,
            name: str,
            vtype: str,
            required: bool = False,
            pname: Optional[str] = None,
            default: Optional[Any] = None,
    ) -> str:
        """Register meta info for a variable.

        Args:
            name: Name of the variable.
            vtype: Type of variable. Allowed values: "core" or "plugin".
            required: Value required or not. Default: False.
            pname: (Optional) Name of defining plugin.
            default: (Optional) Default value of variable.

        Returns:
            Variable name.

        Raises:
            ValueError if wrong vtype and pname.
        """
        if vtype not in ("core", "plugin"):
            raise ValueError
        if vtype == "core" and pname is not None:
            raise ValueError
        if vtype == "plugin" and pname is None:
            raise ValueError

        var = variable_name(pname=pname, name=name)
        meta = {"type": vtype, "required": required, "pname": pname, "default": default}
        # store
        self._name2var[var] = meta
        if pname:
            self._pname2vars.setdefault(pname, {})[var] = meta
        return var

    def register_core_variable(
            self, name: str, required: bool = False, default: Optional[Any] = None
    ) -> str:
        """Register meta info for a general purpose variable.

        .. seealso:: :method:`ConfigMeta._register_var`
        """
        return self.register_variable(
            name=name, vtype="core", required=required, default=default
        )

    def register_plugin_variable(
            self,
            pname: str,
            name: str,
            required: bool = False,
            default: Optional[Any] = None,
    ) -> str:
        """Register meta info for a plugin specific variable.

        .. seealso:: :method:`ConfigMeta._register_var`
        .. seealso:: TODO reference show all variables
        """

        return self.register_variable(
            name=name, vtype="plugin", required=required, pname=pname, default=default
        )

    @property
    def plugin_vars(self) -> Sequence[str]:
        return tuple(
            var_name
            for variables in self._pname2vars.values()
            for var_name in variables
        )

    @property
    def core_vars(self) -> Sequence[str]:
        return tuple(
            var_name for var_name, meta in self._name2var.items() if not meta["pname"]
        )

    @property
    def name2var(self) -> Mapping[str, Any]:
        """Variable name to variable mapping."""
        return dict(self._name2var)

    @property
    def pname2vars(self) -> Mapping[str, Mapping[str, Any]]:
        """Plugin name to variables mapping."""
        return dict(self._pname2vars)

    def set_defaults(self) -> None:
        """Set default values for core and plugin specific variables."""
        self.set_core_defaults()
        self.set_plugin_defaults()

    def set_core_defaults(self) -> None:
        """Set default values for core variables."""
        for var_name in self.core_vars:
            meta = self._name2var[var_name]
            if "default" in meta and var_name not in current_app.config:
                current_app.config[var_name] = meta["default"]

    def set_plugin_defaults(self, pnames: Optional[Sequence[str]] = None) -> None:
        """Set default values for plugin specific variables.

        Args:
            pnames: Plugin names. Default: None
        """
        if pnames is None:
            pnames = list(self._pname2vars.keys())
        for pname in pnames:
            for var_name, meta in self._pname2vars.get(pname, {}).items():
                if "default" in meta and var_name not in current_app.config:
                    current_app.config[var_name] = meta["default"]

    def check_config(self) -> None:
        """Check if all required variables are set."""
        self.check_core_config()
        self.check_plugin_config()

    def check_core_config(self) -> None:
        """Check if required core variables are set.

        Raises:
            :class:`MissingVariable`
        """
        for var_name, meta in self._name2var.items():
            if meta["pname"] is None:
                _check_meta(var_name, meta)

    def check_plugin_config(self, pnames: Optional[Sequence[str]] = None) -> None:
        """Check if plugin specific required variables are set.

        Args:
            pnames: Plugin names. Default: None

        Raises:
            :class:`MissingVariable`
        """
        if pnames is None:
            pnames = list(self._pname2vars.keys())
        for pname in pnames:
            for var_name, meta in self._pname2vars.get(pname, {}).items():
                _check_meta(var_name, meta)


def _check_meta(var_name: str, meta: Mapping[str, Any]) -> None:
    if meta["required"] and (
            var_name not in current_app.config or current_app.config[var_name] is None
    ):
        raise MissingVariable(var_name)


def variable_name(name: str, pname: Optional[str] = None) -> str:
    """Format variable name.

    Args:
        name: Variable name.
        pname: Plugin name. Default: None

    Returns:
        Formatted variable name.
    """

    if pname and not pname.startswith("i-vis-"):
        return f"I_VIS_{pname}_{name}".upper()

    return f"I_VIS_{name}".upper()


def add_i_vis(name: str, value: Any) -> None:
    _flask_config[variable_name(name)] = value


def get_ivis(name: str, default: Optional[Any] = None) -> Any:
    return get_config().get(variable_name(name), default)


def require_ivis(name: str) -> Any:
    return get_config()[variable_name(name)]


def init_app(app: Flask) -> None:
    if app.config:
        _flask_config.update(app.config)


def get_config() -> Mapping[str, Any]:
    return dict(_flask_config)
