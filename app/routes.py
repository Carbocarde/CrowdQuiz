from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User, Question, Answer, Topic, Subject, QuestionTopics, QuestionEval
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, NewQuestionForm, NewTopicForm, DeleteQuestionForm, ReviewQuestionForm, QuizQuestion, NewSubjectForm
from app.email import send_password_reset_email
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random

@app.route('/')
@app.route('/index')
def index():
    subject = Subject.query.filter_by(approved=True).limit(25).all()
    topics = Topic.query.all()

    questionCount = db.session.query(func.count(Question.id), func.avg(Question.evaluations), Subject)\
        .select_from(Subject).filter_by(approved=True).outerjoin(Question).group_by(Subject.id)

    return render_template('index.html', title='Home', subjects=subject, topics=topics, subjectcounts=questionCount)

@app.route('/admin')
@login_required
def admin():
    questions = Question.query.order_by(Question.timestamp).limit(20)
    subjects = Subject.query.limit(25)
    topics = Topic.query.all()

    questionCount = db.session.query(func.count(Question.id), func.avg(Question.evaluations), Subject)\
        .select_from(Subject).outerjoin(Question).group_by(Subject.id)

    return render_template('admin.html', title='Admin Dashboard', subjects=subject, topics=topics, subjectcounts=questionCount, questions=questions)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    questions = Question.query.filter_by(user_id=user.id).order_by(Question.id.desc()).limit(20)
    subjects = Subject.query.limit(25)
    return render_template('user.html', user=user, questions=questions, subjects=subjects)

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
        user = User(username=form.username.data, email=form.email.data, name=form.name.data)
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
        current_user.name = form.name.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
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

@app.route('/suggest_subject')
def suggested_subjects():
    subjects = Subject.query.filter_by(approved=False).limit(25).all()

    return render_template('suggested_subjects.html', subjects=subjects)

@app.route('/suggest_subject/new', methods=['GET', 'POST'])
def suggest_new_subject():
    form = NewSubjectForm()

    if form.validate_on_submit():
        new_subject = Subject(approved=False, body=form.subject.data, description=form.description.data, user_id=current_user.id)
        db.session.add(new_subject)
        db.session.commit()

        return redirect(url_for('suggested_subjects'))

    return render_template('suggest_new_subject.html', form=form)


@app.route('/subject/<subject_id>/new_question', methods=['GET', 'POST'])
@login_required
def new_question(subject_id):
    form = NewQuestionForm(subject_id)

    form.topics.query = Topic.query.filter_by(subject=subject_id).all()

    if form.validate_on_submit():
        new_question = Question()

        new_question = Question(body=form.question.data, author=current_user, subject=subject_id, fairness_score=1, evaluations=1)
        db.session.add(new_question)
        db.session.commit()
        db.session.refresh(new_question)

        for topic in form.topics.data:
            topic_id = topic.id
            classification = QuestionTopics(topic_id=topic_id,question_id=new_question.id)
            db.session.add(classification)

        answers = [None]*4
        answers[0] = Answer(body=form.correct_answer.data, correct=True, question=new_question)
        answers[1] = Answer(body=form.incorrect_answer_1.data, correct=False, question=new_question)
        answers[2] = Answer(body=form.incorrect_answer_2.data, correct=False, question=new_question)
        answers[3] = Answer(body=form.incorrect_answer_3.data, correct=False, question=new_question)

        for answer in answers:
            db.session.add(answer)

        db.session.commit()

        return redirect('/question/' + str(new_question.id))

    subject = Subject.query.filter_by(id=subject_id).first()

    return render_template(
        'new_question.html', form=form, subject=subject
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

@app.route('/subject/<subject_id>', methods=['GET', 'POST'])
@login_required
def subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first_or_404()
    topics = Topic.query.filter_by(subject=subject_id)
    questions = Question.query.filter_by(subject=subject_id)

    form = NewTopicForm()
    if form.validate_on_submit():
        newtopic = Topic(body=form.topic.data, subject=subject_id)
        db.session.add(newtopic)
        db.session.commit()

    return render_template(
        'subject.html',
        subject=subject,
        topics=topics,
        questions=questions,
        form=form
    )

@app.route('/delete_question/<question_id>', methods=['GET', 'POST'])
@login_required
def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first_or_404()
    if not (current_user.id == question.user_id or current_user.admin):
        flash('You do not have permission for this page')
        return redirect(url_for('index'))

    answers = Answer.query.filter_by(question_id=question_id)
    topics = QuestionTopics.query.filter_by(question_id=question_id)
    allTopics = []

    for topic in topics:
        allTopics.append(Topic.query.filter_by(id=topic.topic_id).first())

    form = DeleteQuestionForm()
    if form.validate_on_submit():
        if form.submit.data:
            db.session.delete(question)
            QuestionTopics.query.filter_by(question_id=question_id).delete()
            Answer.query.filter_by(question_id=question_id).delete()
            db.session.commit()
            flash('Question Successfully Deleted.')
            return redirect(url_for('index'))
        if form.cancel.data:
            return redirect(url_for('index'))

    return render_template(
        'delete_question.html',
        question=question,
        topics=allTopics,
        answers=answers,
        form=form
    )

@app.route('/subject/<subject_id>/quiz', methods=['GET', 'POST'])
@login_required
def subject_quiz(subject_id):
    form = QuizQuestion()

    question = Question.query.filter_by(subject=subject_id).order_by(func.random()).first()

    # get answers
    correct_answer = Answer.query.filter_by(question_id=question.id).filter_by(correct=True).order_by(func.random()).limit(1)
    incorrect_answers = Answer.query.filter_by(question_id=question.id).filter_by(correct=False).order_by(func.random()).limit(3)

    form.answers.query = correct_answer.union(incorrect_answers).order_by(func.random()).all()

    if form.submit.data:
        print(form.answers.data)

    return render_template(
        'quiz.html',
        form=form,
        question=question
    )


@app.route('/subject/<subject_id>/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate_questions(subject_id):
    wasSkipped=False
    question = Question.query.filter_by(subject=subject_id).with_entities(Question.id).except_(QuestionEval.query.with_entities(QuestionEval.question_id).filter_by(user_id=current_user.id)).order_by(func.random()).first()
    if (question == None):
        wasSkipped=True
        question = Question.query.filter_by(subject=subject_id).with_entities(Question.id).except_(QuestionEval.query.filter_by(skipped=False).with_entities(QuestionEval.question_id).filter_by(user_id=current_user.id)).order_by(func.random()).first_or_404()

    answers = Answer.query.filter_by(question_id=question.id)

    topics = QuestionTopics.query.filter_by(question_id=question.id)
    allTopics = []

    question = Question.query.filter_by(id=question.id).first()

    for topic in topics:
        allTopics.append(Topic.query.filter_by(id=topic.topic_id).first())

    form = ReviewQuestionForm()

    topics = []
    for topic in allTopics:
        topics.append((topic.id, topic.body))

    # form.topics.choices = topics

    if form.validate_on_submit():
        if form.fair.data or form.unfair.data:
            if wasSkipped:
                evaluation = QuestionEval.query.filter_by(user_id=current_user.id).filter_by(question_id=question.id).first()
                evaluation.fair = form.fair.data
                evaluation.skipped = False
            else:
                evaluation = QuestionEval(user_id=current_user.id, question_id=question.id, fair=form.fair.data, skipped=False)
                db.session.add(evaluation)

            if (question.fairness_score == None):
                score = 1
            else:
                score = question.fairness_score

            if (form.fair.data):
                question.fairness_score = score + 1
            else:
                question.fairness_score = score - 1

            if (question.evaluations == None):
                evaluations = 1
            else:
                evaluations = question.evaluations

            question.evaluations = evaluations + 1

            db.session.commit()
        if form.skip.data:
            if not wasSkipped:
                evaluation = QuestionEval(user_id=current_user.id, question_id=question.id, fair=form.fair.data, skipped=False)
                db.session.add(evaluation)
                db.session.commit()

    return render_template(
        'evaluate_question.html',
        question=question,
        topics=allTopics,
        answers=answers,
        form=form
    )
