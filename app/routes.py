from flask import render_template
from app import app

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
