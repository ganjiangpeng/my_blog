from flask import render_template,session,redirect,url_for,flash,request
from werkzeug.security import generate_password_hash,check_password_hash
from . import auth
from .forms import RegisterForm,LoginForm
from ..models import User,Role
from .. import db
from flask_login import login_user,logout_user



@auth.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role_id=1)
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('register.html',form=form)

@auth.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remeber_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)
@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/test')
def db_test():
    try:
        u1 = User(username='gan',role=Role.query.filter_by(name='Admin').first())
        #r1 = Role(name='User')
        db.session.add(u1)
        db.session.commit()
        return 'check database now'
    except Exception as e:
        return 'faild'

@auth.route('/show')
def show():
    role = Role.query.filter_by(name='Admin').all()
    user = User.query.filter_by(username='gan').all()
    return render_template('show.html',user= user,role=role)

@auth.route('/test1')
def test1():
    u = User()
    u.password = 'cat'
    return  '%s' %u.verify_password('cat')
