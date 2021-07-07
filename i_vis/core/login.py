""" Flask LoginManager plugin.

Import and execute ``login.init_app(app)`` in a factory function to use.

"""

from typing import Any, Callable, TYPE_CHECKING
from functools import wraps

from flask import redirect, request, url_for
from flask_login import current_user
from flask_login.login_manager import LoginManager

from .errors import flash_permission_denied

if TYPE_CHECKING:
    from werkzeug.wrappers import Response

login = LoginManager()


def admin_required(func: Callable) -> Callable:
    """Make view only accessible to admins.

    Args:
        func: Callabe to wrap.

    Returns:
        Wrapped callable - only callable when user is an admin.
    """

    @wraps(func)
    def decorated_view(*args, **kwargs) -> Any:
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
def unauthorized_callback() -> "Response":
    return redirect(url_for("main.signin", next=request.path))
