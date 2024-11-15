# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from .models import User



class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[
        DataRequired(),
        Length(max=150, message="Event name must be 150 characters or fewer.")
    ])
    event_description = TextAreaField('Event Description', validators=[
        DataRequired(),
        Length(max=500, message="Description must be 500 characters or fewer.")
    ])
    date = DateField('Event Date', validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField('Event Time', validators=[DataRequired()], format='%H:%M')
    location = StringField('Event Location', validators=[
        DataRequired(),
        Length(max=200, message="Location must be 200 characters or fewer.")
    ])
    submit = SubmitField('Create Event')