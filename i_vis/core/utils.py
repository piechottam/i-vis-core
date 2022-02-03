"""
General utility classes and methods.
"""

import logging
from datetime import datetime
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    TYPE_CHECKING,
)
from urllib.parse import urlparse, urljoin
import re

from flask import request
from tqdm import tqdm
from requests.exceptions import RequestException

if TYPE_CHECKING:
    from logging import LogRecord
    from .db import db


class StatusCode200Error(RequestException):
    """Status code != 200."""


def is_safe_url(target: str) -> bool:
    """Check if target url is safe.

    Check target url to prevent cross-site scripting attacks.

    Args:
        target: An url check if it is safe.

    Returns:
        True if target is safe or False otherwise.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# TODO adjust
class EnumMixin:
    """Mixin provides convenience methods."""

    @classmethod
    def from_str(cls, s: str) -> Any:
        for v in cls:  # type: ignore
            if v.value == s:
                return v
        raise NotImplementedError

    @classmethod
    def values(cls) -> Set[str]:
        return {e.value for e in cls}  # type: ignore


def format_datetime(value: datetime, format_: str) -> str:
    """TODO-report - a template filter for jinja2

    Args:
        value:
        format_:

    Returns:

    """
    return value.strftime(format_)


def datatable_columns(column_descs: Mapping) -> Sequence[Mapping]:
    """TODO-report somehow needed for datatable

    Args:
        column_descs:

    Returns:

    """
    return tuple(col_desc["dt"] for col_desc in column_descs)


def datatable_render_link(url: str, label: str = "'+data+'") -> str:
    """TODO-report what is this used for?

    Args:
        url:
        label:

    Returns:

    """
    return (
        "function(data, type, row, meta) {"
        f""" if (type === 'display') return '<a href="{url}">{label}</a>'; else return data;"""
        "}"
    )


def render_link(url, label):
    """TODO-report what is this used for?

    Args:
        url:
        label:

    Returns:

    """
    return f'<a href="{url}">{label}</a>'


def table_labels(column_descs: Mapping) -> Mapping:
    """TODO-report somewho needed for datatable

    Args:
        column_descs:

    Returns:

    """
    return {
        col_desc["db"]["data"]: col_desc["db"]["label"]
        for col_desc in column_descs
        if col_desc.get("db") is not None and col_desc["db"]["label"] != ""
    }


# TODO-report what is this for? Make a class from it
_DATATABLE = {}


# TODO-report
def register_datatable_query(
        query_name: str, model, schema, query_desc, callback: Optional[Callable] = None
) -> None:
    if not callback:
        callback = _true
    _DATATABLE[query_name] = {
        "model": model,
        "schema": schema,
        "query_desc": query_desc,
        "callback": callback,
    }


# TODO-report map queries to callbacks. Make a class from it.
_AUTOCOMPLETE: MutableMapping = {}


# TODO-report
def _true() -> bool:
    return True


# TODO-report
def register_autocomplete(
        model_name: str, model: "db.Base", column: str, callback: Optional[Callable] = None
) -> None:
    model_meta = _AUTOCOMPLETE.setdefault(model_name.title(), {})
    if not model_meta:
        model_meta["model"] = model
        model_meta["cols"] = {}

    if callback is None:
        callback = _true
    model_meta["cols"][column] = callback


class TqdmLoggingHandler(logging.StreamHandler):
    """Logging handler for tqdm and multi-threaded application."""

    def emit(self, record: "LogRecord") -> None:
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # pylint: disable=W0702
            self.handleError(record)


CLASS_NAME_REGEX = re.compile("([ _-]*)([^ _-]+)")


def class_name(*names: str) -> str:
    def helper(match: re.Match) -> str:
        return match.group(2)[0].upper() + match.group(2)[1:]

    return "".join(CLASS_NAME_REGEX.sub(helper, name) for name in names)
