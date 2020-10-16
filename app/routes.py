from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Patrick'}
    questions = [
        {
            'author': {'username': 'Patrick'},
            'body': 'What\'s an interval order?'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'When was the battle of Gettysburg?'
        }
    ]
    return render_template('index.html', title='Home', user=user, questions=questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
