from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import ExamTopics
from app.topics import bp
from flask import abort

@bp.route('/class/<class_id>/exam/<exam_id>/topic/<topic_id>/', methods=['GET', 'POST'])
@login_required
def topic(class_id, exam_id, topic_id):
    exam = ExamTopics.query.filter_by(exam_id=exam_id, topic_id=topic_id).first_or_404()

    return render_template('topics/topic.html', exam_topic=exam, overall_level=2)
