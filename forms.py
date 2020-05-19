from flask_wtf import FlaskForm  #extension for using forms in flask
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ideaboard.models import User


class RegistrationForm(FlaskForm):    #Inherits from FlaskForm, this form has diff form fields
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)]) #validator - username should not be empty
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()    #if not present, will be None
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired()])
    description = TextAreaField('Project Description', validators=[DataRequired()])
    effort_required = TextAreaField('Effort Required', validators=[DataRequired()])
    business_value = TextAreaField('Business Value', validators=[DataRequired()])
    submit = SubmitField('Submit')
    #comment = TextAreaField('Comments')
    #accept = SubmitField('Accept')
    #decline = SubmitField('Decline')


class AddCommentForm(FlaskForm):
    comment = StringField("Comment", validators=[DataRequired()])
    #username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Post")

