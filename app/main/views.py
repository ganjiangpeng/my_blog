from . import main
from flask import render_template
@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<name>')
def users(name):
    books=['python','php','java','lua','shell']
    message = {'name':'gan','age':18,'sex':'M'}
    return render_template('users.html',name=name,books=books,message=message)