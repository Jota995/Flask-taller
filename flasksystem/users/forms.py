from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flasksystem.models import User, Area

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                                    validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                                    validators=[DataRequired(), Email()])
    area = SelectField('Area', 
                                    choices=Area.choices(), coerce=Area.coerce)
    password = PasswordField('Password', 
                                    validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('El username ya esta registrado por favor elige uno diferente')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya esta registrado por favor elige uno diferente')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                                    validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                                    validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                                    validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                                    validators=[DataRequired(), Email()])                             
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('El username ya esta registrado por favor elige uno diferente')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ese email ya esta registrado por favor elige uno diferente')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('Password', 
                                    validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])                             
    submit = SubmitField('Update')