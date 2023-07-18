from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea


class CreateApiForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    api_body = StringField('Api Body', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')


class RegisterUserForm(FlaskForm):
    name = StringField('First name', validators=[DataRequired()])
    surname = StringField('Last name', validators=[DataRequired()])
    mail = EmailField('Email', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match!')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Add User')


class LoginUserForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
