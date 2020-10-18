from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User, Question, Answer, Topic, Subject, QuestionTopics
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, NewQuestionForm, NewTopicForm
from app.email import send_password_reset_email

@app.route('/')
@app.route('/index')
@login_required
def index():
    subject = Subject.query.limit(25).all()
    topics = Topic.query.all()

    return render_template('index.html', title='Home', subjects=subject, topics=topics)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    questions = User.query.filter_by(user_id=user.id)
    return render_template('user.html', user=user, questions=questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/subject/<subject_id>/new_question', methods=['GET', 'POST'])
@login_required
def new_question(subject_id):
    form = NewQuestionForm()

    subject_topics = Topic.query.filter_by(subject=subject_id)

    topics = []

    for topic in subject_topics:
        topics.append((topic.id, topic.body))

    form.topics.choices = topics

    if form.validate_on_submit():
        new_question = Question()

        new_question = Question(body=form.question.data, author=current_user, subject=subject_id)
        db.session.add(new_question)
        db.session.commit()

        db.session.refresh(new_question)

        for topic_id in form.topics.data:
            classification = QuestionTopics(topic_id=topic_id,question_id=new_question.id)
            db.session.add(classification)

        correct_answer = Answer(body=form.correct_answer.data, correct=True, question=new_question)

        db.session.add(correct_answer)

        incorrect_answer_1 = Answer(body=form.incorrect_answer_1.data, correct=False, question=new_question)

        db.session.add(incorrect_answer_1)

        incorrect_answer_2 = Answer(body=form.incorrect_answer_2.data, correct=False, question=new_question)

        db.session.add(incorrect_answer_2)

        incorrect_answer_3 = Answer(body=form.incorrect_answer_3.data, correct=False, question=new_question)

        db.session.add(incorrect_answer_3)

        db.session.add(new_question)
        db.session.commit()

        print(form.topics.data)

        return redirect('/question/' + str(new_question.id))

    return render_template(
        'new_question.html', form=form
    )

@app.route('/question/<question_id>', methods=['GET'])
def show_question(question_id):
    """Show the details of a question."""
    question = Question.query.filter_by(id=question_id).first()
    answers = Answer.query.filter_by(question_id=question_id)

    if (question == None):
        return render_template('404.html')

    return render_template(
        'question.html',
        question=question,
        answers=answers
    )

@app.route('/subject/<subject_id>/', methods=['GET', 'POST'])
@login_required
def subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    topics = Topic.query.filter_by(subject=subject_id)

    form = NewTopicForm()
    if form.validate_on_submit():
        newtopic = Topic(body=form.topic.data, subject=subject_id)
        db.session.add(newtopic)
        db.session.commit()

    return render_template(
        'subject.html',
        subject=subject,
        topics=topics,
        form=form
    )

'''
    if (subject == None):
        return render_template('404.html')'''

'''
@app.route('/subject/<subject_id>/quiz', methods=['GET', 'POST'])
@login_required
def new_question(subject_id):'''
