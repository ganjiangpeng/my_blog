#coding=utf-8
from flask_wtf import Form
from wtforms import SubmitField,StringField,PasswordField,IntegerField,SelectField,BooleanField,ValidationError
from wtforms.validators import DataRequired,Email,Length,EqualTo,Regexp
from ..models import User

class RegisterForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(4, 64)])
    username = StringField('username:',validators=[DataRequired(),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                           'Username must have only letters,numbers and *_')])
    password = PasswordField('Password',validators=[DataRequired(),Length(4,32)])
    password2 = PasswordField('Confirm password',validators=[DataRequired(),EqualTo('password',message="Passwrod must match.")])
    #age = IntegerField('age',validators=[DataRequired(),Length(16,100)])
    #sex = SelectField('sex',choices=[('1','woman'),('0','man')])
    #phone = IntegerField('phone',validators=[Length(11)])
    submit = SubmitField('Submit')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered。')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class LoginForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(4,64),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remeber_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')