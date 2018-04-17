#coding:utf-8
from . import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
#flask_login回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
#用户模型
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password_hash = db.Column(db.String(255))
    #create_at = db.Column(db.Integer)
    #last_at = db.Column(db.Integer)
    #phone = db.Column(db.Integer)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)

    #密码加密
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    #密码验证
    def verify_password(self,password):
        #return self.password_hash == password
        return check_password_hash(self.password_hash,password)
    #生成认证令牌
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    #验证令牌
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    def __repr__(self):
        return '<User %r>' % self.username