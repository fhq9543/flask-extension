import os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
from flask_script import Manager
from threading import Thread


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Mail]'
app.config['MAIL_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_RECEIVER'] = os.environ.get('MAIL_RECEIVER')

bootstrap = Bootstrap(app)
moment = Moment(app)
manager = Manager(app)
mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        username=form.name.data
        if app.config['MAIL_RECEIVER']:
            send_email(app.config['MAIL_RECEIVER'], 'New User',
                       'mail/new_user', username=username)
            print('send mail')
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name='word')

if __name__ == '__main__':
    manager.run()
