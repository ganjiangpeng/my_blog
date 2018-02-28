from flask import render_template,session,redirect,url_for,flash
from . import auth
from .forms import RegisterForm

@auth.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['password'] = form.password.data
        flash('It looks ok!')
        return redirect(url_for('.register'))
    return render_template('register.html',form=form,name=session.get('name'),password=session.get('password'))

