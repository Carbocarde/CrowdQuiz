from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User, Question, Answer, Topic, QuestionTopics, QuestionEval, School, Class, Exam, ExamTopics, Enrollment, ExamStructureSuggestion
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, NewQuestionForm, NewTopicForm, DeleteQuestionForm, ReviewQuestionForm, QuizQuestion, NewSubjectForm, EditExamStructureForm, EvaluateQuestionForm, ProposeClassForm, ProposeTopicForm
from app.email import send_password_reset_email
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random

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
    form.school.query = School.query.all()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, name=form.name.data, admin=False, school_id=form.school.data.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    exams = []
    enrolled = []
    enrolled_classes = []
    unenrolled_exams = []
    unenrolled = []
    unenrolled_classes = []

    unenrolled_count = 0
    enrolled_count = 0

    if current_user.is_authenticated:
        classes = Class.query.filter_by(school_id=current_user.school_id, approved=True).limit(25);

        for class_element in classes:
            if db.session.query(Enrollment.id).filter_by(class_id=class_element.id, user_id=current_user.id).scalar() is not None:
                exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
                enrolled.append(True)
                enrolled_classes.append(class_element)
                enrolled_count += 1
            else:
                unenrolled_exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
                unenrolled.append(False)
                unenrolled_classes.append(class_element)
                unenrolled_count += 1

        classes = Class.query.filter_by(school_id=current_user.school_id, approved=False).limit(25);

        for class_element in classes:
            if db.session.query(Enrollment.id).filter_by(class_id=class_element.id, user_id=current_user.id).scalar() is not None:
                exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
                enrolled.append(True)
                enrolled_classes.append(class_element)
                enrolled_count += 1

    else:
        classes = Class.query.filter_by(approved=True).limit(25);

        for class_element in classes:
            unenrolled_exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
            unenrolled.append(False)
            unenrolled_classes.append(class_element)
            unenrolled_count += 1

    return render_template('index.html', title='Home', enrolled_classes = enrolled_count, unenrolled_classes = unenrolled_count, enrolled_class_exams=zip(enrolled_classes, exams, enrolled), unenrolled_class_exams=zip(unenrolled_classes, unenrolled_exams, unenrolled))

@app.route('/suggested_classes/')
@login_required
def suggested_classes():
    exams = []
    enrolled = []
    enrolled_classes = []
    unenrolled_exams = []
    unenrolled = []
    unenrolled_classes = []

    unenrolled_count = 0
    enrolled_count = 0

    if current_user.is_authenticated:
        classes = Class.query.filter_by(school_id=current_user.school_id, approved=False).limit(25);

        for class_element in classes:
            if db.session.query(Enrollment.id).filter_by(class_id=class_element.id, user_id=current_user.id).scalar() is not None:
                exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
                enrolled.append(True)
                enrolled_classes.append(class_element)
                enrolled_count += 1
            else:
                unenrolled_exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
                unenrolled.append(False)
                unenrolled_classes.append(class_element)
                unenrolled_count += 1

    else:
        classes = Class.query.filter_by(approved=False).limit(25);

        for class_element in classes:
            unenrolled_exams.append(Exam.query.filter_by(class_id = class_element.id).limit(9))
            unenrolled.append(False)
            unenrolled_classes.append(class_element)
            unenrolled_count += 1

    return render_template('suggested_classes.html', title='Proposed Classes', enrolled_classes = enrolled_count, unenrolled_classes = unenrolled_count, enrolled_class_exams=zip(enrolled_classes, exams, enrolled), unenrolled_class_exams=zip(unenrolled_classes, unenrolled_exams, unenrolled))

@app.route('/suggested_classes/propose_class', methods=['GET', 'POST'])
@login_required
def propose_class():
    form = ProposeClassForm()

    if form.validate_on_submit():
        new_class = Class(approved=False, body=form.body.data, readable=form.title.data, description=form.description.data, user_id=current_user.id, school_id=current_user.school_id)
        db.session.add(new_class)
        db.session.commit()

        return redirect(url_for('suggested_classes'))

    return render_template('suggest_class.html', form=form)

@app.route('/class/<class_id>/')
@login_required
def class_(class_id):
    class_element = Class.query.filter_by(id=class_id).first_or_404();

    exams = Exam.query.filter_by(class_id = class_id)

    exam_topics = []
    for exam in exams:
        exam_topics.append(ExamTopics.query.filter_by(exam_id=exam.id).limit(9))

    return render_template('class.html', title=class_element.body, class_element=class_element, exam_topics_all=zip(exams, exam_topics))

@app.route('/class/<class_id>/suggest_exam_structure/', methods=['GET', 'POST'])
@login_required
def suggested_exam_structure(class_id):

    class_element = Class.query.filter_by(id=class_id).first_or_404();

    form = EditExamStructureForm();
    if form.validate_on_submit():
        exam_structure = ExamStructureSuggestion(body=form.comment.data, exam_count=form.exams.data, quiz_count=form.quizzes.data, final_exam=form.final_exam.data, final_exam_cumulative=form.final_exam_cumulative.data, user_id=current_user.id, class_id=class_id, approved=False)
        db.session.add(exam_structure)
        db.session.commit()

        flash('Your suggestion has been recieved!')
        return redirect(url_for('class_', class_id=class_id))

    return render_template('suggest_exam_structure.html', title='Proposed Exams', class_element=class_element, form=form)

@app.route('/class/<class_id>/exam/<exam_id>/suggested_topics/', methods=['GET', 'POST'])
@login_required
def suggested_topics(class_id, exam_id):

    exam = Exam.query.filter_by(id = exam_id).first_or_404()

    exam_topics = ExamTopics.query.filter_by(exam_id=exam.id).limit(25)

    unfollowed_topics = 0
    question_count = []
    for exam_topic in exam_topics:
        unfollowed_topics += 1
        question_count.append(db.session.query(QuestionTopics.query.filter_by(topic_id=exam_topic.topic.id).subquery()).count())

    return render_template('suggested_topics.html', title='Proposed Topics', exam=exam, exam_topic_question_counts=zip(exam_topics, question_count), unfollowed_topics=unfollowed_topics)

@app.route('/class/<class_id>/exam/<exam_id>/suggested_topics/propose_new', methods=['GET', 'POST'])
@login_required
def suggest_topic(class_id, exam_id):
    form = ProposeTopicForm()

    exam = Exam.query.filter_by(id=exam_id).first_or_404()

    if form.validate_on_submit():
        new_topic = Topic(body=form.body.data, description=form.description.data)
        db.session.add(new_topic)
        db.session.commit()
        db.session.refresh(new_topic)

        new_exam_topics = ExamTopics(exam_id=exam_id, topic_id=new_topic.id)
        db.session.add(new_exam_topics)
        db.session.commit()

        return redirect(url_for('suggested_topics', class_id=class_id, exam_id=exam_id))

    return render_template('suggest_topic.html', form=form, exam=exam)

@app.route('/class/<class_id>/enroll/')
@login_required
def enroll(class_id):
    class_element = Class.query.filter_by(id=class_id).first_or_404();

    evaluation = Enrollment(user_id=current_user.id, class_id=class_id)
    db.session.add(evaluation)
    db.session.commit()

    return redirect(url_for('class_', class_id=class_id))

@app.route('/class/<class_id>/exam/<exam_id>/')
@login_required
def exam(class_id, exam_id):
    exam = Exam.query.filter_by(id = exam_id).first_or_404()

    exam_topics = ExamTopics.query.filter_by(exam_id=exam.id).limit(25)

    question_count = []
    for exam_topic in exam_topics:
        question_count.append(db.session.query(QuestionTopics.query.filter_by(topic_id=exam_topic.topic.id).subquery()).count())

    return render_template('exam.html', title="Exam", exam=exam, exam_topic_question_counts=zip(exam_topics, question_count))

@app.route('/class/<class_id>/exam/<exam_id>/contribute/', defaults={'topic_id': None})
@app.route('/class/<class_id>/exam/<exam_id>/topic/<topic_id>/contribute/')
@login_required
def contribute(class_id, exam_id, topic_id):

    exam = Exam.query.filter_by(id=exam_id).first_or_404()

    topic = None

    if topic_id is not None:
        topic = Topic.query.filter_by(id=topic_id).first_or_404()
        question_topics = QuestionTopics.query.filter_by(topic_id=topic_id)

    forms = []
    questions = []
    topics = []

    for question_topic in question_topics:
        print("ok")
        questions.append(question_topic.question)
        topics = QuestionTopics.query.filter_by(question_id = question_topic.question.id)
        forms.append(EvaluateQuestionForm())

    return render_template('contribute.html', title="Contribute", exam=exam, topic=topic, evaluation_forms=zip(forms, questions, topics))

@app.route('/admin')
@login_required
def admin():
    if not current_user.admin:
        return render_template('404.html')

    pending_exam_structures = ExamStructureSuggestion.query.filter_by(approved=False).limit(20)
    classes = Class.query.filter_by(approved=False).limit(20)
    questions = Question.query.order_by(Question.timestamp).limit(20)

    topics = []
    for question in questions:
        topics.append(QuestionTopics.query.filter_by(question_id = question.id))

    return render_template('admin.html', title='Admin Dashboard', question_topics=zip(questions,topics), exam_structure_suggestions=pending_exam_structures, classes=classes)

@app.route('/class/<class_id>/approve')
@login_required
def approve_class(class_id):
    if not current_user.admin:
        return render_template('404.html')

    class_element = Class.query.filter_by(id=class_id).first_or_404()
    class_element.approved = True
    db.session.commit()

    flash('Class ' + class_element.body + " Approved!")
    return redirect(url_for('admin'))

@app.route('/exam_structure/<exam_structure_id>/approve')
@login_required
def approve_exam_structure(exam_structure_id):
    if not current_user.admin:
        return render_template('404.html')

    structure = ExamStructureSuggestion.query.filter_by(id=exam_structure_id).first_or_404()

    for i in range(1, structure.exam_count):
        new_exam = Exam(body="Exam " + str(i), class_id=structure.class_id, exam_number = i)
        db.session.add(new_exam)
        db.session.commit()

    if structure.final_exam:
        new_exam = Exam(body="Final Exam", class_id=structure.class_id, exam_number = structure.exam_count + 1, cumulative=structure.final_exam_cumulative)
        db.session.add(new_exam)
        db.session.commit()

    structure.approved = True
    db.session.commit()

    flash('Exam structure added for ' + structure.exam_class.body)
    return redirect(url_for('admin'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    questions = Question.query.filter_by(user_id=user.id).order_by(Question.id.desc()).limit(20)
    enrollments = Enrollment.query.filter_by(user_id=user.id).limit(20)

    exams = []
    classes = []

    unenrolled_exams = []
    unenrolled_classes = []
    for enrollment in enrollments:
        if enrollment.enrolled_class.approved:
            classes.append(enrollment.enrolled_class)
            exams.append(Exam.query.filter_by(class_id=enrollment.class_id))
        else:
            unenrolled_classes.append(enrollment.enrolled_class)
            unenrolled_exams.append(Exam.query.filter_by(class_id=enrollment.class_id))


    return render_template('user.html', user=user, questions=questions, class_exams=zip(classes, exams), enrolled=(len(exams) > 0), unenrolled_class_exams=zip(unenrolled_classes, unenrolled_exams), unenrolled=(len(exams) > 0))

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

@app.route('/subject/<subject_id>/new_question', methods=['GET', 'POST'])
@login_required
def new_question(subject_id):
    form = NewQuestionForm(subject_id)

    form.topics.query = Topic.query.filter_by(subject_id=subject_id).all()

    if form.validate_on_submit():
        new_question = Question()

        new_question = Question(body=form.question.data, author=current_user, subject_id=subject_id, fairness_score=1, evaluations=1)
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
        'new_question.html', form=form, subject_id=subject
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
    topics = Topic.query.filter_by(subject_id=subject_id)
    questions = Question.query.filter_by(subject_id=subject_id)

    form = NewTopicForm()
    if form.validate_on_submit():
        newtopic = Topic(body=form.topic.data, subject_id=subject_id)
        db.session.add(newtopic)
        db.session.commit()

    return render_template(
        'subject.html',
        subject_id=subject,
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

    question = Question.query.filter_by(subject_id=subject_id).order_by(func.random()).first()

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
    question = Question.query.filter_by(subject_id=subject_id).with_entities(Question.id).except_(QuestionEval.query.with_entities(QuestionEval.question_id).filter_by(user_id=current_user.id)).order_by(func.random()).first()
    if (question == None):
        wasSkipped=True
        question = Question.query.filter_by(subject_id=subject_id).with_entities(Question.id).except_(QuestionEval.query.filter_by(skipped=False).with_entities(QuestionEval.question_id).filter_by(user_id=current_user.id)).order_by(func.random()).first_or_404()

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
