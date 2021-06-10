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
    name = StringField("Username", validators=[DataRequired()])
    email = StringField(
        "E-Mail",
        validators=[
            DataRequired(),
            Email(message="Enter a valid email."),
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
    current = PasswordField("Current Password", validators=[DataRequired()])


class SignInForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    rememberme = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "E-Mail",
        validators=[
            DataRequired(),
            Email(message="Enter E-Mail of your account."),
        ],
    )
    submit = SubmitField("Send")


class PasswordRecoveryForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Select a stronger passwort."),
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
    name = StringField("Username", validators=[DataRequired()])
    email = StringField(
        "E-Mail",
        validators=[
            DataRequired(),
            Email(message="Enter a valid email."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Select a stronger passwort."),
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
