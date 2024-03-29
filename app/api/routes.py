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

    question_text = question.strip()
    answer_text = answer.strip()

    # Instantly reject empty/invalid terms
    if (question is None or question_text == "" or answer is None or answer_text == ""):
        return jsonify({'empty': True})

    exam = Exam.query.filter_by(id=exam_id).first_or_404()

    topic = None

    duplicate = False

    # Check if idential question entry already exists
    question = Question.query.filter_by(body=question_text).first()

    # Check if identical answer entry already exists
    answer = Answer.query.filter_by(body=answer_text).first()

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
        question = Question(user_id=current_user.id, body=question_text)
        db.session.add(question)
        db.session.commit()
        db.session.refresh(question)

        # Add question to general topic
        question_topic = QuestionTopics(question_id=question.id, topic_id=general_topic.topic.id)
        db.session.add(question_topic)
        db.session.commit()

    # Generate an answer entry if one was not found prior
    if answer is None:
        answer = Answer(user_id=current_user.id, body=answer_text)
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

    # Remove prior set item if new term is not a duplicate of the previous item in that slot
    if not duplicate and prior_id != -1:
        removeterm = StudySetTerm.query.filter_by(id=prior_id).first()
        if removeterm is not None:
            db.session.delete(removeterm)
            db.session.commit()

    return jsonify({'id': term.id, 'duplicate': duplicate, 'empty': False})

@bp.route('/api/v1.0/deleteterm', methods=['POST'])
@login_required
def deleteterm():
    term_id = request.form['term_id']

    term = StudySetTerm.query.filter_by(id=term_id).first()

    term_sets = StudySetTerm.query.filter_by(question_answer_id=term.question_answer.id).count()

    # if this is the only reference to the question/answer relation
    if term_sets == 1:
        db.session.delete(term.question_answer)

    if term is not None:
        db.session.delete(term)

    db.session.commit()

    return jsonify({})

@bp.route('/api/v1.0/altans', methods=['POST'])
@login_required
def altans():
    term_id = request.form['term_id']

    term = StudySetTerm.query.filter_by(id=term_id).first()
    question_id = term.question_answer.question.id
    answers = QuestionAnswer.query.filter_by(question_id=question_id)

    body = []
    id = []
    for answer in answers:
        body.append(answer.answer.body)
        id.append(answer.answer.id)

    db.session.commit()

    return jsonify({ 'ids' : id, 'bodys' : body })

@bp.route('/api/v1.0/flashcards/save_progress', methods=['POST'])
@login_required
def studyset():
    exam_id = request.form['exam_id']
    term_ids = request.form.getlist('term_ids[]')
    term_status = request.form.getlist('term_status[]')
    term_interactions = request.form.getlist('term_interactions[]')

    terms = zip(term_ids, term_status, term_interactions)

    for term in terms:
        term_entry = StudySetTerm.query.filter_by(id=term[0]).first()

        status = int(term[1])
        if (status >= -1 and status <= 3):
            term_entry.saved_status = status

        interactions = int(term[2])
        if (interactions >= 0):
            term_entry.interaction_count += interactions

    db.session.commit()

    return jsonify({})

@bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
