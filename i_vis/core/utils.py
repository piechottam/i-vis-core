from enum import Enum
from functools import wraps
from typing import Callable, Mapping, MutableMapping, Optional, Sequence, Set
from urllib.parse import urlparse, urljoin
import logging

from flask import redirect, request, url_for
from flask_login import current_user
from tqdm import tqdm

from . import login
from .errors import flash_permission_denied


def is_safe_url(targets):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, targets))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


class EnumMixin:
    @classmethod
    def from_str(cls, s: str):
        return EnumUtils.from_str(cls, s)

    @classmethod
    def values(cls) -> Set["str"]:
        return EnumUtils.values(cls)


class EnumUtils:
    @staticmethod
    def from_str(enum: Enum, s: str):
        for e in enum:
            if e.value == s:
                return e
        raise NotImplementedError

    @staticmethod
    def values(enum: Enum) -> Set["str"]:
        # pylint: disable=E1133
        return {e.value for e in enum}


def datetime_format(value, format_: str) -> str:
    return value.strftime(format_)


def datatable_columns(column_descs: Mapping) -> Sequence[Mapping]:
    return tuple(col_desc["dt"] for col_desc in column_descs)


def datatable_render_link(url: str, label: str = "'+data+'") -> str:
    return (
        "function(data, type, row, meta) {"
        f""" if (type === 'display') return '<a href="{url}">{label}</a>'; else return data;"""
        "}"
    )


def render_link(url, label):
    return f'<a href="{url}">{label}</a>'


def table_labels(column_descs: Mapping) -> Mapping:
    return {
        col_desc["db"]["data"]: col_desc["db"]["label"]
        for col_desc in column_descs
        if col_desc.get("db") is not None and col_desc["db"]["label"] != ""
    }


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if (
            current_user is None
            or not current_user.is_authenticated
            or not current_user.is_admin
        ):
            flash_permission_denied()
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return decorated_view


@login.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("main.signin", next=request.path))


_DATATABLE = {}


def register_datatable_query(
    query_name: str, model, schema, query_desc, callback: Optional[Callable] = None
):
    if not callback:
        callback = _true
    _DATATABLE[query_name] = {
        "model": model,
        "schema": schema,
        "query_desc": query_desc,
        "callback": callback,
    }


_AUTOCOMPLETE: MutableMapping = {}


def _true():
    return True


def register_autocomplete(
    model_name: str, model, column: str, callback: Optional[Callable] = None
):
    model_meta = _AUTOCOMPLETE.setdefault(model_name.title(), {})
    if not model_meta:
        model_meta["model"] = model
        model_meta["cols"] = {}

    if callback is None:
        callback = _true
    model_meta["cols"][column] = callback


class TqdmLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # pylint: disable=W0702
            self.handleError(record)
