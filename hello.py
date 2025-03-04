from flask import Flask,  request, make_response, abort, render_template, redirect, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin prof.seeyouholler@gmail.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')



bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
    sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    
    
    


@app.route('/', methods = ['GET', 'POST'])
def index():
    # user_agent = request.headers.get('User-Agent')
    resp = make_response('<p>Bad Request</p>')
    resp.set_cookie('answer', '43')
    # user = load_user(id)
    # if not user:
    #     abort()
    
    form = NameForm()
    if form.validate_on_submit():
        # old_name = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        # if old_name is not None and old_name != form.name.data:
        if user is None:
            # flash('Looks you have changed your name')
            user = User(username=form.name.data)
            db.session.add(user)
            # db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email('FLASKY_ADMIN', 'New User', 'mail/new_user', user=user)
                
        else:
            session['known'] = True
             
        session['name'] = form.name.data
        form.name.data =''
        
        return redirect(url_for('index'))
    return render_template('index.html',
current_time=datetime.utcnow(), form=form,  known=session.get('known', False), name=session.get('name'))
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'Role {self.name}'
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    
    def __repr__(self):
        return f'User {self.username}'

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


    
if __name__ == '__main__':
    app.run(debug=True)