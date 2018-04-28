#coding:utf-8
from flask_wtf import Form
from wtforms import SubmitField,StringField,PasswordField,TextAreaField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,Regexp,ValidationError
from ..models import Role,User
from flask_pagedown.fields import PageDownField

#普通用户修改信息表单
class EditProfileForm(Form):
    name = StringField('Name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

#管理员修改用户信息表单
class EditProfileAdminForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(4,64),Email()])
    username = StringField('Username',validators=[DataRequired(),
                                                  Length(1,64),
                                                  Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                         'Usernames must have only letters numbers,dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role',coerce=int)
    name = StringField('Name',validators=[Length(1,64)])
    location = StringField('Location',validators=[Length(1,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name,) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already regisered.')

class PostForm(Form):
    body = PageDownField("what's on your mind?",validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('',validators=[DataRequired()])
    submit = SubmitField('Submit')


class ReplyForm(Form):
    body = StringField('',validators=[DataRequired()])
    submit = SubmitField('Submit')

