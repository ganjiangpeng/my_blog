from flask_wtf import Form
from wtforms import SubmitField,StringField,PasswordField
from wtforms.validators import Required

class RegisterForm(Form):
    name = StringField('username:',validators=[Required()])
    password = PasswordField('Password',validators=[Required()])
    submit = SubmitField('Submit')