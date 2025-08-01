from app import app
from flask import render_template,flash,redirect,url_for
from app.forms import LoginForm
from app.models import User
from flask_login import current_user,login_user,logout_user,login_required
import sqlalchemy as sa
from app import db
from flask import request
from urllib.parse import urlsplit
from app.forms import RegistrationForm
from datetime import datetime,timezone
from app.forms import Editprofileform


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Sainath'}
    posts = [
        {
            'author': {'username': 'sainath'},
            'body': 'locke was right'
        },
        {
            'author': {'username': 'sumit'},
            'body': 'The Dark was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user= db.session.scalar(
            sa.select(User).where(User.username==form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("invalid username or data")
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page=request.args.get('next')
        if not next_page or urlsplit(next_page).netloc !='':
            next_page=url_for('index')
        return redirect(next_page)
    
    
    return render_template('login.html', title='sign.in', form=form)

@app.route('/logout')
def logout():   
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        flash("congratulation you are a new user")
        return redirect(url_for('login'))
    return render_template('register.html',title="register",form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.before_request
def befor_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = Editprofileform()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)