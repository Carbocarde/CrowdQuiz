from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import User, Question, Answer, Topic, QuestionTopics, QuestionEval, School, Class, Exam, ExamTopics, Enrollment, ExamStructureSuggestion, QuestionAnswer, QuestionAnswerArgument, FollowExamTopic
from app.user.forms import EditProfileForm
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random
from collections import namedtuple
from sqlalchemy.orm import load_only
from app.user import bp
from flask import abort

@bp.route('/admin')
@login_required
def admin():
    if not current_user.admin:
        abort(404)

    pending_exam_structures = ExamStructureSuggestion.query.filter_by(approved=False).limit(20)
    classes = Class.query.filter_by(approved=False).limit(20)
    questions = Question.query.order_by(Question.timestamp).limit(20)

    topics = []
    for question in questions:
        topics.append(QuestionTopics.query.filter_by(question_id = question.id))

    return render_template('user/admin.html', title='Admin Dashboard', question_topics=zip(questions,topics), exam_structure_suggestions=pending_exam_structures, classes=classes)

@bp.route('/user/<username>/')
@login_required
def user_profile(username):
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

    return render_template('user/user.html', user=user, questions=questions, class_exams=zip(classes, exams), enrolled=(len(exams) > 0), unenrolled_class_exams=zip(unenrolled_classes, unenrolled_exams), unenrolled=(len(exams) > 0))

@bp.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user.user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
    return render_template('user/edit_profile.html', title='Edit Profile',
                           form=form)
