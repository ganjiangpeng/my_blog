from flask_mail import Message
from flask import render_template,current_app
from . import mail

def send_email(to,subject,template,**kwargs):
    app=current_app._get_current_object()
    msg = Message(subject,sender=app.config['FLASK_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    mail.send(msg)