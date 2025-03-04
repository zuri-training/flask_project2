from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, abort, request, current_app, make_response
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Role, Permission, Post
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries

@main.route('/', methods=['GET', 'POST'])
def index():
    # form = NameForm()
    form = PostForm()
    # if form.validate_on_submit():
        
    
        
        
        # old_name = session.get('name')
        # user = User.query.filter_by(username=form.name.data).first()
        # if old_name is not None and old_name != form.name.data:
        # if user is None:
        #     # flash('Looks you have changed your name')
        #     user = User(username=form.name.data)
        #     db.session.add(user)
        #     # db.session.commit()
        #     session['known'] = False
            # if app.config['FLASKY_ADMIN']:
            #     send_email('FLASKY_ADMIN', 'New User', 'mail/new_user', user=user)
                
        # else:
        #     session['known'] = True
             
        # session['name'] = form.name.data
        # form.name.data =''
        
        # return redirect(url_for('.index'))
    
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
        author=current_user.getcurrent_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    return render_template('index.html', current_time=datetime.utcnow(), form=form, posts=posts)
    # return render_template('index.html',
    #     current_time=datetime.utcnow(), form=form, posts=posts, known=session.get('known', False), name=session.get('name'))
    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
        
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.   username))
    
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

# @main.route('/', methods=['GET', 'POST'])
# def index():
#     form = PostForm()
#     if current_user.can(Permission.WRITE) and form.validate_on_submit():
#         post = Post(body=form.body.data,
#         author=current_user.getcurrent_object())
#         db.session.add(post)
#         db.session.commit()
#         return redirect(url_for('.index'))
#     posts = Post.query.order_by(Post.timestamp.desc()).all()
#     return render_template('index.html', form=form, posts=posts)