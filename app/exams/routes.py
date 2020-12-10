from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import User, Question, Answer, Topic, QuestionTopics, QuestionEval, School, Class, Exam, ExamTopics, Enrollment, ExamStructureSuggestion, QuestionAnswer, QuestionAnswerArgument
from app.exams.forms import ExamShortAnswerQuestion, OpenEndedAnswerEval
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random
from collections import namedtuple
from sqlalchemy.orm import load_only
from app.exams import bp
from app.models import OpenEndedQuestionAttempt, QuestionAnswer

@bp.route('/class/<class_id>/exam/<exam_id>/exam/', methods=['GET', 'POST'])
@login_required
def exam(class_id, exam_id):
    exam = Exam.query.filter_by(id = exam_id, class_id = class_id).first_or_404()

    question = Question.query.order_by(func.random()).first_or_404()

    form = ExamShortAnswerQuestion();

    if form.validate_on_submit():
        qAnswer = QuestionAnswer.query.filter_by(question_id=question.id).order_by(QuestionAnswer.correctness_score).first_or_404()

        questionAttempt = OpenEndedQuestionAttempt(user_id=current_user.id, question_id=question.id, answer_id=qAnswer.answer.id, body=form.answer.data)
        db.session.add(questionAttempt)
        db.session.commit()
        db.session.refresh(questionAttempt)

        return redirect(url_for('exams.attempt', exam_id=exam_id, class_id=class_id, attempt_id=questionAttempt.id))

    return render_template('exams/short_answer_question.html', title="Exam", exam=exam, question=question, form=form)

@bp.route('/class/<class_id>/exam/<exam_id>/exam/<attempt_id>/', methods=['GET', 'POST'])
@login_required
def attempt(class_id, exam_id, attempt_id):
    exam = Exam.query.filter_by(id = exam_id, class_id = class_id).first_or_404()

    attempt = OpenEndedQuestionAttempt.query.filter_by(id=attempt_id).first_or_404()

    form = OpenEndedAnswerEval();

    if form.validate_on_submit():
        if form.next.data:
            return redirect(url_for('exams.exam', exam_id=exam_id, class_id=class_id))
        elif form.submit.data:
            return redirect(url_for('main.exam', exam_id=exam_id, class_id=class_id))

    return render_template('exams/short_answer_question_result.html', attempt=attempt, exam=exam, form=form)
