from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import User, Question, Answer, Topic, QuestionTopics, QuestionEval, School, Class, Exam, ExamTopics, Enrollment, ExamStructureSuggestion, QuestionAnswer, QuestionAnswerArgument, Section
from app.teacher.forms import AddExamForm, EditExamForm
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random
from collections import namedtuple
from sqlalchemy.orm import load_only
from app.teacher import bp

@bp.route('/teacher/')
@login_required
def index():
    if not current_user.teacher:
        return render_template('errors/404.html')

    sections = Section.query.filter_by(user_id=current_user.id)

    exams = []
    for section in sections:
        exams.append(Exam.query.filter_by(section_id=section.id))

    return render_template('teacher/index.html', title='Home', section_exams=zip(sections, exams))

@bp.route('/section/<section_id>/claim/')
@login_required
def claim_section(section_id):
    section = Section.query.filter_by(id=section_id).first_or_404()
    if section.user_id or not current_user.teacher:
        return render_template('errors/404.html')

    section.user_id = current_user.id
    db.session.add(section)
    db.session.commit()

    flash('Class Section' + section.body + ' claimed!')
    return redirect(url_for('teacher.manage_section', section_id=section_id))

@bp.route('/section/<section_id>/manage/')
@login_required
def manage_section(section_id):
    if not current_user.teacher:
        return render_template('errors/404.html')
    section = Section.query.filter_by(id=section_id).first_or_404()
    if not section.user_id:
        flash('Claim section before attempting to manage it!')
        redirect(url_for('main.section', section_id=section_id))
    if section.user_id != current_user.id:
        return render_template('errors/404.html')

    exams = Exam.query.filter_by(section_id=section_id).order_by(Exam.exam_number)

    topics = []
    for exam in exams:
        exam_topics = ExamTopics.query.filter_by(exam_id=exam.id)
        topics.append(exam_topics)

    invite_link = url_for('main.section_invite', section_id=section.id)

    return render_template('teacher/manage_section.html', section=section, exams=exams, exam_topics=zip(exams, topics), invite_link=invite_link)

@bp.route('/section/<section_id>/add_exam/', methods=['GET', 'POST'])
@login_required
def add_exam(section_id):
    section = Section.query.filter_by(id=section_id).first_or_404()
    if not current_user.teacher or not section.user_id or section.user_id != current_user.id:
        return render_template('errors/404.html')

    exams_count = Exam.query.count()

    form = AddExamForm()
    if form.validate_on_submit():
        exam = Exam(body=form.exam_title.data, exam_number=form.exam_number.data, cumulative=form.cumulative.data, section_id=section_id)
        db.session.add(exam)
        db.session.commit()
        flash('Your exam has been saved.')
        return redirect(url_for('teacher.manage_section', section_id=section_id))
    elif request.method == 'GET':
        form.exam_number.data = exams_count + 1
        form.exam_title.data = 'Exam ' + str(exams_count + 1)

    return render_template('teacher/add_exam.html', section=section, form=form)

@bp.route('/exam/<exam_id>/edit_exam/', methods=['GET', 'POST'])
@login_required
def edit_exam(exam_id):
    exam = Exam.query.filter_by(id=exam_id).first_or_404()
    section = Section.query.filter_by(id=exam.section.id).first_or_404()
    if not current_user.teacher or not section.user_id or section.user_id != current_user.id:
        return render_template('errors/404.html')

    form = EditExamForm()
    if form.validate_on_submit():
        exam.body = form.exam_title.data
        exam.exam_number = form.exam_number.data
        exam.cumulative = form.cumulative.data
        db.session.add(exam)
        db.session.commit()
        flash('Your exam has been saved.')
        return redirect(url_for('teacher.manage_section', section_id=section.id))
    elif request.method == 'GET':
        form.exam_number.data = exam.exam_number
        form.exam_title.data = exam.body
        form.cumulative.data = exam.cumulative

    return render_template('teacher/edit_exam.html', section=section, form=form, exam=exam)
