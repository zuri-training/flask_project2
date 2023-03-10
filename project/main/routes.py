from templates.static.main import app, db
from flask import render_template, url_for, redirect, flash, request, session
from project.models import User, Role
from project.main.forms import NameForm
from flask_mail import Message, Mail

app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

        else:
            session['known'] = True

        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

