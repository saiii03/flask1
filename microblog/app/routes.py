from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'sumit'}
    posts = [
        {'author': {'username': 'sumit'}, 'body': "the red is actually blue"},
        {'author': {'username': 'sakshi'}, 'body': "colors is how you see it"}
    ]
    return render_template('index.html', title='home', user=user, posts=posts)
