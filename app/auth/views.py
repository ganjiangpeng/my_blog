#coding:utf-8
from flask import render_template,session,redirect,url_for,flash,request,abort
from werkzeug.security import generate_password_hash,check_password_hash
from . import auth
from .forms import RegisterForm,LoginForm,ChangePasswordForm,PasswordResetForm,PasswordResetRequestForm,TestForm
from ..models import User,Role,Permission
from .. import db
from flask_login import login_user,logout_user,login_required,current_user
from ..mail import send_email
from ..decorators import permission_required,admin_required

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
    if not current_user.is_anonymous:
        flash('You are old man.')
        return redirect(url_for('main.index'))
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
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
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


@auth.route('/change_password',methods=["POST",'GET'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash("Your password has been updated.")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid password.")
    return render_template("auth/change_password.html",form=form)

@auth.route('/reset',methods=['POST','GET'])
def reset_password_request():
    #if current_user.is_anonymous:
    #    return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email,'Reset Your Password',
                       'auth/email/reset_password',
                       token=token,user=user,
                       next=request.args.get('next'))
        flash('An Email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['POST','GET'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)







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

@auth.route('/test_role')
def add_role():
    return current_user.role.name
@auth.route('/test_decorator')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def test_decorator():
    return 'must be admin to see this!'

@auth.route('/test_p')
def test_p():
    current_user.ping()
    return 'time is sync'

@auth.route('/test_form',methods=['POST','GET'])
def test_form():
    form = TestForm()
    if form.validate_on_submit():
        return "%s" %form.test.data
    return render_template('test.html',form=form)


@auth.route('/editor')
def editor():
    return render_template('editor.html')

