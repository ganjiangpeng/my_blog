#coding:utf-8
from . import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from datetime import datetime
import hashlib
#flask_login回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#权限类
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x03
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

#用户角色
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')

#添加角色/修改角色
    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW|
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW|
                        Permission.COMMENT|
                         Permission.WRITE_ARTICLES|
                         Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
            db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

# 关联者模型
class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    followed = db.relationship('Follow',
                              foreign_keys=[Follow.follower_id],
                              backref=db.backref('follower',lazy='joined'),
                              lazy='dynamic',
                              cascade='all,delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref = db.backref('followed',lazy='joined'),
                                lazy='dynamic',
                                cascade='all,delete-orphan')

    comments = db.relationship('Comment',backref='author',lazy="dynamic")
    replys = db.relationship('Reply',backref='author',lazy="dynamic")

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
    #生成重置密码的token
    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id})
    #验证重置密码token,通过后修改密码
    def reset_password(self,token,new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True
    #个用户设置角色，如果是特定用户，则设置为admin
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None  and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
    #角色权限判断，用给定的权限与自己的权限，判断是否有相应权限
    def can(self,permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
    #判断是否为管理员用户
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    #更新最后登录时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    def __repr__(self):
        return '<User %r>' % self.username
    #生成头像连接
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://secure.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,hash=hash,size=size,default=default,rating=rating)

    #关注
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)
    #取消关注
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    #是否已关注user
    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    #是否被user关注
    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)


#文章模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    comments = db.relationship('Comment',backref='post',lazy='dynamic')

class Comment(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
    disabled = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    replys = db.relationship('Reply',backref='comment',lazy='dynamic')

class Reply(db.Model):
    __tablename__ = "replys"
    id = db.Column(db.Integer,primary_key=True)
    pids = db.Column(db.String,index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer,db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled = db.Column(db.Boolean,default=True)



class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser
