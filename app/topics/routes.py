from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import ExamTopics, Question, QuestionTopics, QuestionEval
from app.topics import bp
from flask import abort
from sqlalchemy.orm import load_only

@bp.route('/class/<class_id>/exam/<exam_id>/topic/<topic_id>/', methods=['GET', 'POST'])
@login_required
def topic(class_id, exam_id, topic_id):
    exam_topic = ExamTopics.query.filter_by(exam_id=exam_id, topic_id=topic_id).first_or_404()

    topic_questions = QuestionTopics.query.filter_by(topic_id=exam_topic.topic.id).subquery()

    # Select questions that have been evaluated by this user
    current_user_questions = Question.query.filter_by(user_id=current_user.id).options(load_only(Question.id)).subquery()
    current_user_evaluated = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id).subquery()

    # Select questions that user has submitted to this topic
    user_topic_questions = QuestionTopics.query.filter_by(topic_id=exam_topic.topic_id).filter(QuestionTopics.question_id.in_(current_user_questions)).subquery()

    current_user_topic_evaluations = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id).outerjoin(topic_questions, topic_questions.c.question_id == QuestionEval.question_id).filter_by(topic_id=exam_topic.topic_id).subquery()

    unlock_percent = db.session.query(current_user_topic_evaluations).count() * 5 + db.session.query(user_topic_questions).count() * 25
    question_count = db.session.query(topic_questions).count()

    level_subtractor = 0
    i = unlock_percent - 100
    j = 0
    while i > 0:
        level_subtractor += (100 + 5 * j)
        i = i - (100 + 5 * j)
        j += 1

    level = j + 1

    return render_template('topics/topic.html', exam_topic=exam_topic, level=level, percent=unlock_percent, level_subtractor=level_subtractor, question_count=question_count)
