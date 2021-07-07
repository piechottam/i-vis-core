"""
Main routes.

"""

from flask import abort, Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_login.utils import login_required

from ..db import db
from ..forms import SignInForm, ChangeUserForm
from ..models import User, Setting
from ..utils import is_safe_url
from ..login import admin_required

bp = Blueprint("main", __name__)


@bp.route("/index", methods=["GET", "POST"])
@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("home.jinja", current_user=current_user)


@bp.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", category="error")
            return redirect(url_for("main.signin"))
        login_user(user, remember=form.rememberme.data)

        next_ = request.args.get("next")
        if not next_ or not is_safe_url(next_):
            return abort(400)

        return redirect(next_ or url_for("main.index"))
    return render_template("signin.jinja", form=form)


@bp.route("/signout")
@login_required
def signout():
    if current_user.is_authenticated:
        logout_user()
        flash("Sign out successful.", category="success")
    return redirect(url_for("main.signin"))


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    #     if current_user.is_authenticated:
    #         return redirect(url_for("main.index"))
    #     form = ForgotPasswordForm()
    #     if form.validate_on_submit():
    #         user = User.query.filter_by(mail=form.mail.data).first()
    #         if user is None:
    #             flash("Unknown E-Mail.", category="error")
    #             return redirect(url_for("main.password_recovery"))
    #         # create code
    #         # write E-MAIL TODO send e-mail
    #         # link with
    #         flash(
    #             f"Instruction to recover password have been sent to: {form.mail.data}",
    #             category="info",
    #         )
    #         return redirect(url_for("main.signin"))
    return render_template("forgot_password_no_mail.jinja")


# @bp.route("/password-recovery", methods=["GET", "POST"])
# def password_recovery():
#    token = request.args.get("token")
#    user = User.query.filter_by(token=token).first()
#    if user is None:
#        flash("Unknown token - password recovery failed.", category="error")
#        return redirect(url_for("main.forgot_password"))
#    form = PasswordRecoveryForm()
#    if form.validate_on_submit():
#        user.set_password(form.password.data)
#        db.session.add(user)
#        db.session.commit()
#        flash("Password changed. Try to Sign in.", category="success")
#        return redirect(url_for("main.signin"))
#    return render_template("password-recovery.jinja", form=form, token=token)


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = ChangeUserForm(obj=current_user)
    if form.validate_on_submit():
        if form.password.data and current_user.check_password(form.current.data):
            current_user.set_password(form.password.data)
            db.session.add(current_user)
            db.session.commit()
            flash("Password changed.", category="success")
            return render_template("account.jinja", form=form)

        flash("Current password incorrect.", category="error")
        return render_template("account.jinja", form=form)
    return render_template("account.jinja", form=form)


@bp.route("/settings", methods=["GET", "POST"])
@admin_required
@login_required
def show_settings():
    settings = {
        setting.variable: str(setting.value)
        for setting in Setting.query.order_by(Setting.variable).all()
    }
    return render_template(
        "settings.jinja", settings=settings, current_user=current_user
    )
