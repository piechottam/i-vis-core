"""
I-VIS core forms

User management
"""
from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length


class UserForm(FlaskForm):
    """Form for essential user account info"""

    name = StringField("Username", validators=[DataRequired()])
    mail = StringField(
        "E-Mail",
        validators=[
            DataRequired(),
            Email(message="Enter a valid mail."),
        ],
    )
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
        ],
    )
    confirm = PasswordField(
        "Confirm New Password",
        validators=[
            EqualTo("password", message="Passwords must match."),
        ],
    )


class ChangeUserForm(UserForm):
    """Form based on :class:`UserForm` with additional validation."""

    current = PasswordField("Current Password", validators=[DataRequired()])


class SignInForm(FlaskForm):
    """Signin form."""

    name = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    rememberme = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class ForgotPasswordForm(FlaskForm):
    """Forgot my password form."""

    mail = StringField(
        "E-Mail",
        validators=[
            DataRequired(),
            Email(message="Enter E-Mail of your account."),
        ],
    )
    submit = SubmitField("Send")


class PasswordRecoveryForm(FlaskForm):
    """Password recovery form."""

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Select a stronger password."),
        ],
    )
    confirm = PasswordField(
        "Confirm Your Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Change")


class RegisterForm(FlaskForm):
    """Register a new account form."""

    name = StringField("Username", validators=[DataRequired()])
    mail = StringField(
        "E-Mail",
        validators=[
            DataRequired(),
            Email(message="Enter a valid mail."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Select a stronger password."),
        ],
    )
    confirm = PasswordField(
        "Confirm Your Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Register")
