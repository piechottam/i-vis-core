from typing import Any, Mapping, Optional

from flask import jsonify, flash


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: Optional[int] = None, payload: Any = None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> Mapping[str, Any]:
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


class DuplicateError(InvalidUsage):
    def __init__(self, entity: str) -> None:
        super().__init__(f"{entity} already exists.")


class NotFoundError(InvalidUsage):
    def __init__(self, entity: str) -> None:
        super().__init__(f"{entity} not fount.", 404)


class IllegalAccessError(InvalidUsage):
    def __init__(self) -> None:
        super().__init__("Permission deniet.", 400)


class MissingDataError(InvalidUsage):
    def __init__(self, entity) -> None:
        super().__init__(f"Missing {entity}.", 400)


def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def flash_permission_denied(extra: Optional[str] = None):
    msg = "Permission deniet."
    if extra is not None:
        msg += extra
    flash(msg, category="error")


def flash_duplicate(
    entity: str, value: Optional[Any] = None, extra: Optional[str] = None
) -> None:
    if value is None:
        msg = f"{entity} already exists."
    else:
        msg = f'{entity}: "{str(value)}" already exists.'
    if extra is not None:
        msg += extra
    flash(msg, category="error")


def flash_not_found(entity: str, value: Any, extra: Optional[str] = None) -> None:
    msg = f'{entity}: "{str(value)}" not fount.'
    if extra is not None:
        msg += extra
    flash(msg, category="error")
