#coding:utf-8
from flask import render_template,session,redirect,url_for,flash,request
from werkzeug.security import generate_password_hash,check_password_hash
from . import auth
from .forms import RegisterForm,LoginForm
from ..models import User,Role
from .. import db
from flask_login import login_user,logout_user,login_required,current_user
from ..mail import send_email

@auth.before_app_request
def befor_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static':
        return redirect(url_for("auth.unconfirmed"))

@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous and current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")

@auth.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role_id=1,confirmed=False)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account',
                   'auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

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

@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account.Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))
@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account',
               'auth/email/confirm',token=token,user=current_user)
    flash("A new confirmation email has been send to you by email.")
    return redirect(url_for("main.index"))














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
