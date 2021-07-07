"""
User specific routes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, Response
from flask_login import current_user
from flask_login.utils import login_required

from ..db import db
from ..errors import flash_duplicate, flash_not_found
from ..forms import ChangeUserForm, UserForm
from ..models import User
from ..login import admin_required

bp = Blueprint("users", __name__, url_prefix="/users")


# TODO
_index_col_descs = {
    "id": "User ID",
    "name": "Username",
    "mail": "E-Mail",
    "created_at": "Created",
    "is_admin": "Admin",
}


@bp.route("/index", methods=["GET", "POST"])
@bp.route("/", methods=["GET", "POST"])
@admin_required
@login_required
def index() -> str:
    return render_template(
        "users/index.jinja",
        column_descs=_index_col_descs,
        current_user=current_user,
    )


@bp.route("/add", methods=["GET", "POST"])
@admin_required
@login_required
def add() -> Response:
    form = UserForm()
    if form.validate_on_submit():
        user = User.load_by_name(form.name.data)
        if user is not None:
            flash_duplicate("Username", extra=" Pick something else.")
            return redirect(url_for("users.add"))
        user = User.load_by_mail(form.mail.data)
        if user is not None:
            flash_duplicate("E-Mail", extra=" Pick something else.")
            return redirect(url_for("users.add"))
        user = User(name=form.name.data, mail=form.mail.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"User {user.name} has been created.", category="success")
        return redirect(url_for("users.show", user_id=user.name))
    return render_template("users/adt.jinja", title="Add User", form=form)


@bp.route("/show/<int:user_id>", methods=["GET", "POST"])
@admin_required
@login_required
def show(user_id: int):
    user_id = int(user_id)
    user = User.query.get(user_id)
    if user is None:
        flash_not_found("User", user_id)
        return redirect(url_for("users.index"))
    return render_template("users/show.jinja", title=f"User {user.name}", user=user)


@bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@admin_required
@login_required
def edit(user_id: int):
    form = ChangeUserForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        if user is None:
            flash_not_found("User", user_id)
            return redirect(url_for("users.index"))
        # prevent duplicates
        tmp_user = User.load_by_name(form.name.data)
        if tmp_user is not None and tmp_user.name != user.name:
            flash_duplicate("User", user_id)
            return redirect(url_for("users.edit"))
        tmp_user = User.load_by_mail(form.mail.data)
        if tmp_user is not None and tmp_user.name != user.name:
            flash_duplicate("E-Mail", form.mail.data)
            return redirect(url_for("users.edit"))
        user = User(name=form.name.data, mail=form.mail.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"User {user.name} has been updated.", category="success")
        return redirect(url_for("users.show", user_id=user.name))
    return render_template("users/edit.jinja", title="Edit User", form=form)
