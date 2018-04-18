#coding:utf-8
from flask_wtf import Form
from wtforms import SubmitField,StringField,PasswordField,IntegerField,SelectField,BooleanField,ValidationError,TextField
from wtforms.validators import DataRequired,Email,Length,EqualTo,Regexp
from ..models import User
#注册表单
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
            raise ValidationError('Email already registered.')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
#登录表单
class LoginForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(4,64),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remeber_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')
#登录之后的修改密码表单
class ChangePasswordForm(Form):
    old_password = PasswordField('Old Password',validators=[DataRequired()])
    new_password = PasswordField('New Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired()])
    submit = SubmitField('Submit')
#忘记密码请求表单
class PasswordResetRequestForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(4,64),Email()])
    submit = SubmitField('Send Email')
#重置密码表单
class PasswordResetForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(4,64),Email()])
    password = PasswordField('New Password',
                             validators=[DataRequired(),
                             EqualTo('password2',message="Password must match.")])
    password2 = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('Reset')


class TestForm(Form):
    test = SelectField('select',coerce=int)
    submit = SubmitField('Submit')

    def __init__(self):
        super(TestForm,self).__init__()
        self.test.choices=[(1,'python'),(3,'java'),(5,'php')]





