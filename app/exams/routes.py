from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import User, Question, Answer, Topic, QuestionTopics, QuestionEval, School, Class, Exam, ExamTopics, Enrollment, ExamStructureSuggestion, QuestionAnswer, QuestionAnswerArgument, FollowExamTopic
from app.exams.forms import ExamShortAnswerQuestion
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random
from collections import namedtuple
from sqlalchemy.orm import load_only
from app.exams import bp

@bp.route('/class/<class_id>/exam/<exam_id>/exam/', methods=['GET', 'POST'])
@login_required
def exam(class_id, exam_id):
    exam = Exam.query.filter_by(id = exam_id, class_id = class_id).first_or_404()

    question = Question.query.first_or_404()

    form = ExamShortAnswerQuestion();

    if form.validate_on_submit():

        return redirect(url_for('main.exam', class_id=class_id, exam_id=exam_id))

    return render_template('exams/short_answer_question.html', title="Exam", exam=exam, question=question, form=form)
