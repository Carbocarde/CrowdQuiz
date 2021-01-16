from flask import render_template, flash, redirect, url_for, request, jsonify, make_response
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.api import bp
from app.models import User, School, Exam, Question, QuestionAnswer, Answer, ExamTopics, Topic, QuestionTopics, StudySetTerm

@bp.route('/api/v1.0/questionanswer', methods=['POST'])
@login_required
def questionanswer():
    question = request.form['qbody']
    answer = request.form['abody']
    exam_id = request.form['exam_id']
    prior_id = request.form['prior_id']

    if (question == ""):
        return jsonify({'id': -1, 'duplicate': True})

    exam = Exam.query.filter_by(id=exam_id).first_or_404()

    topic = None

    duplicate = False

    # Check if idential question entry already exists
    question = Question.query.filter_by(body=request.form['qbody']).first()

    # Check if identical answer entry already exists
    answer = Answer.query.filter_by(body=request.form['abody']).first()

    # Generate a question entry if one was not found prior
    if question is None:
        # Get General topic ready to have the Question added to it
        # Check if General topic exists
        general_topic = db.session.query(ExamTopics).filter_by(exam_id=exam.id).join(Topic, ExamTopics.topic).filter_by(body="All").first()

        # Create general topic if one wasn't found
        if general_topic is None:
            topic = Topic(body="All", description="A place for all questions that fit into this exam")
            db.session.add(topic)
            db.session.commit()
            db.session.refresh(topic)

            general_topic = ExamTopics(exam_id=exam.id, topic_id=topic.id)
            db.session.add(general_topic)
            db.session.commit()

        # Create Question
        question = Question(user_id=current_user.id, body=request.form['qbody'])
        db.session.add(question)
        db.session.commit()
        db.session.refresh(question)

        # Add question to general topic
        question_topic = QuestionTopics(question_id=question.id, topic_id=general_topic.topic.id)
        db.session.add(question_topic)
        db.session.commit()

    # Generate an answer entry if one was not found prior
    if answer is None:
        answer = Answer(user_id=current_user.id, body=request.form['abody'])
        db.session.add(answer)
        db.session.commit()
        db.session.refresh(answer)

    # At this point, there are definately valid question/answer db entries
    # Check if question-answer relation exists
    question_answer = QuestionAnswer.query.filter_by(question_id=question.id, answer_id=answer.id).first()

    if question_answer is not None:

        # Check if term is in current study set
        term = StudySetTerm.query.filter_by(user_id=current_user.id, question_answer_id=question_answer.id, exam_id=exam.id).first()

        if term is not None:
            # Congrats! this is a duplicate entry for this user.
            duplicate = True
        else:
            # Add term to set - everything else is already done
            term = StudySetTerm(user_id=current_user.id, question_answer_id=question_answer.id, exam_id=exam.id)
            db.session.add(term)
            db.session.commit()
            db.session.refresh(term)

    else:
        # if the Question-Answer relation doesn't exist, add it here
        question_answer = QuestionAnswer(question_id=question.id, answer_id=answer.id)
        db.session.add(question_answer)
        db.session.commit()
        db.session.refresh(question_answer)

        # Add term to set
        term = StudySetTerm(user_id=current_user.id, question_answer_id=question_answer.id, exam_id=exam.id)
        db.session.add(term)
        db.session.commit()
        db.session.refresh(term)

    # Remove prior set item if new term is not a duplicate of the previous
    if not duplicate and prior_id != -1:
        removeterm = StudySetTerm.query.filter_by(id=prior_id).first()
        if removeterm is not None:
            db.session.delete(removeterm)
            db.session.commit()

    return jsonify({'id': term.id, 'duplicate': duplicate})

@bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
