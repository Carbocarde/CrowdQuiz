from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import User, Question, Answer, Topic, QuestionTopics, QuestionEval, School, Class, Exam, ExamTopics, Enrollment, ExamStructureSuggestion, QuestionAnswer, QuestionAnswerArgument, FollowExamTopic
from app.main.forms import NewQuestionForm, NewTopicForm, DeleteQuestionForm, ReviewQuestionForm, QuizQuestion, NewSubjectForm, EditExamStructureForm, EvaluateQuestionSubForm, ContributeForm, ProposeClassForm, ProposeTopicForm, NewQuestionForm
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random
from collections import namedtuple
from sqlalchemy.orm import load_only
from app.main import bp

@bp.route('/')
@bp.route('/index')
@bp.route('/home')
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

    return render_template('main/index.html', title='Home', enrolled_classes = enrolled_count, unenrolled_classes = unenrolled_count, enrolled_class_exams=zip(enrolled_classes, exams, enrolled), unenrolled_class_exams=zip(unenrolled_classes, unenrolled_exams, unenrolled))

@bp.route('/suggested_classes/')
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

    return render_template('main/suggested_classes.html', title='Proposed Classes', enrolled_classes = enrolled_count, unenrolled_classes = unenrolled_count, enrolled_class_exams=zip(enrolled_classes, exams, enrolled), unenrolled_class_exams=zip(unenrolled_classes, unenrolled_exams, unenrolled))

@bp.route('/suggested_classes/propose_class', methods=['GET', 'POST'])
@login_required
def propose_class():
    form = ProposeClassForm()

    if form.validate_on_submit():
        new_class = Class(approved=False, body=form.body.data, readable=form.title.data, description=form.description.data, user_id=current_user.id, school_id=current_user.school_id)
        db.session.add(new_class)
        db.session.commit()

        return redirect(url_for('main.suggested_classes'))

    return render_template('main/suggest_class.html', form=form)

@bp.route('/class/<class_id>/')
@login_required
def class_(class_id):
    class_element = Class.query.filter_by(id=class_id).first_or_404();

    exams = Exam.query.filter_by(class_id = class_id)

    enrollment_element = Enrollment.query.filter_by(user_id=current_user.id, class_id=class_id).first()
    if enrollment_element is None:
        enrolled = False
    else:
        enrolled = True

    exam_topics = []
    for exam in exams:
        exam_topics.append(ExamTopics.query.filter_by(exam_id=exam.id).limit(9))

    return render_template('main/class.html', title=class_element.body, enrolled=enrolled, class_element=class_element, exam_topics_all=zip(exams, exam_topics))

@bp.route('/class/<class_id>/suggest_exam_structure/', methods=['GET', 'POST'])
@login_required
def suggested_exam_structure(class_id):

    class_element = Class.query.filter_by(id=class_id).first_or_404();

    form = EditExamStructureForm();
    if form.validate_on_submit():
        exam_structure = ExamStructureSuggestion(body=form.comment.data, exam_count=form.exams.data, quiz_count=form.quizzes.data, final_exam=form.final_exam.data, final_exam_cumulative=form.final_exam_cumulative.data, user_id=current_user.id, class_id=class_id, approved=False)
        db.session.add(exam_structure)
        db.session.commit()

        flash('Your suggestion has been recieved!')
        return redirect(url_for('main.class_', class_id=class_id))

    return render_template('main/suggest_exam_structure.html', title='Proposed Exams', class_element=class_element, form=form)

@bp.route('/class/<class_id>/exam/<exam_id>/suggested_topics/', methods=['GET', 'POST'])
@login_required
def suggested_topics(class_id, exam_id):
    exam = Exam.query.filter_by(id = exam_id).first_or_404()

    exam_topics = ExamTopics.query.filter_by(exam_id=exam.id).limit(25)

    question_count = []
    unlock_percent = []
    following = []
    level_subtractor = []
    level = []
    followed_exam_topics = []
    unfollowed_topics_count = 0
    for exam_topic in exam_topics:
        follow_exam_topic = FollowExamTopic.query.filter_by(user_id=current_user.id, exam_topic_id=exam_topic.id).first()
        if follow_exam_topic is None:
            following.append(False)

            unfollowed_topics_count += 1

            followed_exam_topics.append(exam_topic)

            topic_questions = QuestionTopics.query.filter_by(topic_id=exam_topic.topic.id).subquery()

            # Select questions that have been evaluated by this user
            current_user_questions = Question.query.filter_by(user_id=current_user.id).options(load_only(Question.id)).subquery()
            current_user_evaluated = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id).subquery()

            # Select questions that user has submitted to this topic
            user_topic_questions = QuestionTopics.query.filter_by(topic_id=exam_topic.topic_id).filter(QuestionTopics.question_id.in_(current_user_questions)).subquery()

            current_user_topic_evaluations = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id).outerjoin(topic_questions, topic_questions.c.question_id == QuestionEval.question_id).filter_by(topic_id=exam_topic.topic_id).subquery()

            unlock_percent_element = db.session.query(current_user_topic_evaluations).count() * 5 + db.session.query(user_topic_questions).count() * 25
            unlock_percent.append(unlock_percent_element)
            question_count.append(db.session.query(topic_questions).count())

            level_subtractor_element = 0
            i = unlock_percent_element - 100
            j = 0
            while i > 0:
                level_subtractor_element += (100 + 5 * j)
                i = i - (100 + 5 * j)
                j += 1

            level_subtractor.append(level_subtractor_element)
            level.append(j + 1)

    return render_template('main/suggested_topics.html', title='Proposed Topics', exam=exam, exam_topic_question_counts=zip(followed_exam_topics, question_count, unlock_percent, level, level_subtractor, following), unfollowed_topics=unfollowed_topics_count)

@bp.route('/class/<class_id>/exam/<exam_id>/suggested_topics/propose_new', methods=['GET', 'POST'])
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

        return redirect(url_for('main.suggested_topics', class_id=class_id, exam_id=exam_id))

    return render_template('main/suggest_topic.html', form=form, exam=exam)

@bp.route('/class/<class_id>/enroll/')
@login_required
def enroll(class_id):
    class_element = Class.query.filter_by(id=class_id).first_or_404();

    enrollment_element = Enrollment.query.filter_by(user_id=current_user.id, class_id=class_id).first();

    if enrollment_element is None:
        evaluation = Enrollment(user_id=current_user.id, class_id=class_id)
        db.session.add(evaluation)
        db.session.commit()

    return redirect(url_for('main.class_', class_id=class_id))

@bp.route('/class/<class_id>/unenroll/')
@login_required
def unenroll(class_id):
    class_element = Class.query.filter_by(id=class_id).options(load_only(Class.id)).first_or_404();

    evaluation = Enrollment.query.filter_by(user_id=current_user.id, class_id=class_id).first_or_404();
    db.session.delete(evaluation)
    db.session.commit()

    return redirect(url_for('main.class_', class_id=class_id))

@bp.route('/class/<class_id>/exam/<exam_id>/')
@login_required
def exam(class_id, exam_id):
    exam = Exam.query.filter_by(id = exam_id, class_id = class_id).first_or_404()

    exam_topics = ExamTopics.query.filter_by(exam_id=exam.id).limit(25)

    question_count = []
    unlock_percent = []
    following = []
    level_subtractor = []
    level = []
    followed_exam_topics = []
    for exam_topic in exam_topics:
        follow_exam_topic = FollowExamTopic.query.filter_by(user_id=current_user.id, exam_topic_id=exam_topic.id).first()
        if follow_exam_topic is not None:
            following.append(True)

            followed_exam_topics.append(exam_topic)

            topic_questions = QuestionTopics.query.filter_by(topic_id=exam_topic.topic.id).subquery()

            # Select questions that have been evaluated by this user
            current_user_questions = Question.query.filter_by(user_id=current_user.id).options(load_only(Question.id)).subquery()
            current_user_evaluated = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id).subquery()

            # Select questions that user has submitted to this topic
            user_topic_questions = QuestionTopics.query.filter_by(topic_id=exam_topic.topic_id).filter(QuestionTopics.question_id.in_(current_user_questions)).subquery()

            current_user_topic_evaluations = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id).outerjoin(topic_questions, topic_questions.c.question_id == QuestionEval.question_id).filter_by(topic_id=exam_topic.topic_id).subquery()

            unlock_percent_element = db.session.query(current_user_topic_evaluations).count() * 5 + db.session.query(user_topic_questions).count() * 25
            unlock_percent.append(unlock_percent_element)
            question_count.append(db.session.query(topic_questions).count())

            level_subtractor_element = 0
            i = unlock_percent_element - 100
            j = 0
            while i > 0:
                level_subtractor_element += (100 + 5 * j)
                i = i - (100 + 5 * j)
                j += 1

            level_subtractor.append(level_subtractor_element)
            level.append(j + 1)

    if (len(unlock_percent) > 0):
        overall_unlock_percent = sum(unlock_percent)/len(unlock_percent)
    else:
        overall_unlock_percent = 0

    overall_level_subtractor = 0
    i = overall_unlock_percent - 100
    j = 0
    while i > 0:
        overall_level_subtractor += (100 + 5 * j)
        i = i - (100 + 5 * j)
        j += 1

    overall_level = j + 1

    return render_template('main/exam.html', title="Exam", exam=exam, overall_unlock_percent=overall_unlock_percent, overall_level_subtractor=overall_level_subtractor, overall_level=overall_level, exam_topic_question_counts=zip(followed_exam_topics, question_count, unlock_percent, level, level_subtractor, following))

@bp.route('/class/<class_id>/exam/<exam_id>/contribute/', defaults={'topic_id': None}, methods=['GET', 'POST'])
@bp.route('/class/<class_id>/exam/<exam_id>/topic/<topic_id>/contribute/', methods=['GET', 'POST'])
@login_required
def contribute(class_id, exam_id, topic_id):

    exam = Exam.query.filter_by(id=exam_id).first_or_404()

    topic = None
    if topic_id is not None:
        topic = Topic.query.filter_by(id=topic_id).first_or_404()
    else:
        topic = ExamTopics.query.filter_by(exam_id=exam_id).first_or_404().topic

    contribute = namedtuple('Contribute', ['fair', 'accurate_topics'])

    form = ContributeForm(obj=contribute)

    # Select questions that haven't been evaluated by this user and weren't submitted by them
    current_user_questions = Question.query.filter_by(user_id=current_user.id).options(load_only(Question.id)).subquery()
    current_user_evaluated = db.session.query(QuestionEval.question_id).filter_by(user_id=current_user.id, skipped=False).subquery()
    skippedSubtable = QuestionEval.query.filter_by(user_id=current_user.id).options(load_only(QuestionEval.skipped, QuestionEval.question_id)).subquery()

    question_topics = QuestionTopics.query.filter_by(topic_id=topic.id).filter(QuestionTopics.question_id.notin_(current_user_questions)).filter(QuestionTopics.question_id.notin_(current_user_evaluated)).outerjoin(skippedSubtable, skippedSubtable.c.question_id == QuestionTopics.question_id).order_by(skippedSubtable.c.skipped.desc())

    forms = []
    questions = []

    max_questions = 4
    i = 0

    for question_topic in question_topics:
        if max_questions > i:
            questions.append(question_topic.question)
            i += 1

    evaluation_requests = []
    evaluate_questions = []
    evaluate_topics = []
    if len(form.evaluate_entries) == 0:
        for i in range(0, len(questions)):
            form.evaluate_entries.append_entry()
            evaluate_questions.append(questions[i])
            evaluate_topics.append(QuestionTopics.query.filter_by(question_id=questions[i].id))

    results = []
    if form.validate_on_submit():
        if form.submit.data:
            j=0
            for eval in form.evaluate_entries:
                if eval.skip.data:
                    question_eval = QuestionEval(question_id=questions[j].id, user_id=current_user.id, skipped=True)
                else:
                    question_eval = QuestionEval(question_id=questions[j].id, user_id=current_user.id, skipped=False, fair=eval.fair.data)

                    # TODO: increase connection_score in question_topics

                db.session.add(question_eval)
                db.session.commit()

                j += 1
            flash('Question Evaluations Submitted!.')
            return redirect(url_for('main.exam', class_id=class_id, exam_id=exam_id))

    return render_template('main/contribute_eval.html', title="Contribute", exam=exam, topic=topic, form=form, evaluate_forms=zip(form.evaluate_entries, evaluate_questions, evaluate_topics), eval_questions=len(evaluate_questions))

@bp.route('/class/<class_id>/exam/<exam_id>/contribute/question/', defaults={'topic_id': None}, methods=['GET', 'POST'])
@bp.route('/class/<class_id>/exam/<exam_id>/topic/<topic_id>/contribute/question/', methods=['GET', 'POST'])
@login_required
def contribute_question(class_id, exam_id, topic_id):

    exam = Exam.query.filter_by(id=exam_id).first_or_404()

    topic = None

    if topic_id is not None:
        topic = Topic.query.filter_by(id=topic_id).first_or_404()

    form = NewQuestionForm();
    if form.validate_on_submit():
        question = Question.query.filter_by(body=form.question.data).first()

        found_question_answer = False

        # Check if idential question entry already exists
        if question is not None:
            question_answers = QuestionAnswer.query.filter_by(question_id=question.id)

            # Iterate through to see if the answer/questionanswer relation already exists
            for question_answer in question_answers:
                if question_answer.answer.body == form.correct_answer.data:
                    found_question_answer = True

            # Create the answer entry and questionanswer relation
            if not found_question_answer:
                answer = Answer.query.filter_by(body=form.correct_answer.data).first()

                if not answer:
                    answer = Answer(body=form.correct_answer.data, user_id=current_user.id)
                    db.session.add(answer)
                    db.session.commit()
                    db.session.refresh(answer)

                question_answer = QuestionAnswer(question_id=question.id, answer_id=answer.id)
                db.session.add(question_answer)
                db.session.commit()
                db.session.refresh(question_answer)

        # Generate question entry
        else:
            question = Question(user_id=current_user.id, body=form.question.data)
            db.session.add(question)
            db.session.commit()
            db.session.refresh(question)

            if topic:
                question_topic = QuestionTopics(question_id=question.id, topic_id=topic.id)
            else:
                exam_topic = ExamTopics.query.filter_by(exam_id=exam.id).first()
                if exam_topic:
                    question_topic = QuestionTopics(question_id=question.id, topic_id=exam_topic.topic.id)
                else:
                    topic = Topic(body="General Questions", description="A place for general questions that fit into this exam")
                    db.session.add(topic)
                    db.session.commit()
                    db.session.refresh(topic)

                    exam_topic = ExamTopics(exam_id=exam.id, topic_id=topic.id)
                    db.session.add(exam_topic)
                    db.session.commit()

                    question_topic = QuestionTopics(question_id=question.id, topic_id=topic.id)

            db.session.add(question_topic)
            db.session.commit()

            answer = Answer.query.filter_by(body=form.correct_answer.data).first()

            if not answer:
                answer = Answer(body=form.correct_answer.data, user_id=current_user.id)
                db.session.add(answer)
                db.session.commit()
                db.session.refresh(answer)

            question_answer = QuestionAnswer(question_id=question.id, answer_id=answer.id)
            db.session.add(question_answer)
            db.session.commit()
            db.session.refresh(question_answer)

        flash('Question Contributed!')
        return redirect(url_for('main.contribute_question', class_id=class_id, exam_id=exam_id, topic_id=topic_id))

    return render_template('main/contribute_question.html', title='Contribute', topic=topic, exam=exam, form=form)

@bp.route('/class/<class_id>/exam/<exam_id>/topic/<topic_id>/follow/')
@login_required
def follow_topic(class_id, exam_id, topic_id):
    class_element = Class.query.filter_by(id=class_id).first_or_404();

    exam_topic = ExamTopics.query.filter_by(topic_id=topic_id, exam_id=exam_id).options(load_only(ExamTopics.id)).first_or_404()

    follow_element = FollowExamTopic.query.filter_by(exam_topic_id=exam_topic.id, user_id=current_user.id).first()

    if follow_element is None:
        follow_exam_topic = FollowExamTopic(user_id=current_user.id, exam_topic_id=exam_topic.id)
        db.session.add(follow_exam_topic)
        db.session.commit()

    return redirect(url_for('main.exam', class_id=class_id, exam_id=exam_id))

@bp.route('/admin')
@login_required
def admin():
    if not current_user.admin:
        return render_template(url_for('errors.404'))

    pending_exam_structures = ExamStructureSuggestion.query.filter_by(approved=False).limit(20)
    classes = Class.query.filter_by(approved=False).limit(20)
    questions = Question.query.order_by(Question.timestamp).limit(20)

    topics = []
    for question in questions:
        topics.append(QuestionTopics.query.filter_by(question_id = question.id))

    return render_template('main/admin.html', title='Admin Dashboard', question_topics=zip(questions,topics), exam_structure_suggestions=pending_exam_structures, classes=classes)

@bp.route('/class/<class_id>/approve')
@login_required
def approve_class(class_id):
    if not current_user.admin:
        return render_template('errors.404')

    class_element = Class.query.filter_by(id=class_id).first_or_404()
    class_element.approved = True
    db.session.commit()

    flash('Class ' + class_element.body + " Approved!")
    return redirect(url_for('main.admin'))

@bp.route('/exam_structure/<exam_structure_id>/approve')
@login_required
def approve_exam_structure(exam_structure_id):
    if not current_user.admin:
        return render_template('errors.404')

    structure = ExamStructureSuggestion.query.filter_by(id=exam_structure_id).first_or_404()

    for i in range(1, structure.exam_count):
        exam = Exam(body="Exam " + str(i), class_id=structure.class_id, exam_number = i)
        db.session.add(exam)
        db.session.commit()
        db.session.refresh(exam)

        topic = Topic(body="General Questions", description="A place for general questions that fit into this exam")
        db.session.add(topic)
        db.session.commit()
        db.session.refresh(topic)

        exam_topic = ExamTopics(exam_id=exam.id, topic_id=topic.id)
        db.session.add(exam_topic)
        db.session.commit()

    if structure.final_exam:
        exam = Exam(body="Final Exam", class_id=structure.class_id, exam_number = structure.exam_count + 1, cumulative=structure.final_exam_cumulative)
        db.session.add(exam)
        db.session.commit()

        topic = Topic(body="General Questions", description="A place for general questions that fit into the Final Exam")
        db.session.add(topic)
        db.session.commit()
        db.session.refresh(topic)

        exam_topic = ExamTopics(exam_id=exam.id, topic_id=topic.id)
        db.session.add(exam_topic)
        db.session.commit()

    structure.approved = True
    db.session.commit()

    flash('Exam structure added for ' + structure.exam_class.body)
    return redirect(url_for('main.admin'))

@bp.route('/delete_question/<question_id>', methods=['GET', 'POST'])
@login_required
def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first_or_404()
    if not (current_user.id == question.user_id or current_user.admin):
        flash('You do not have permission for this page')
        return redirect(url_for('main.index'))

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
            return redirect(url_for('main.index'))
        if form.cancel.data:
            return redirect(url_for('main.index'))

    return render_template(
        'main/delete_question.html',
        question=question,
        topics=allTopics,
        answers=answers,
        form=form
    )

@bp.route('/subject/<subject_id>/evaluate', methods=['GET', 'POST'])
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
        'main/evaluate_question.html',
        question=question,
        topics=allTopics,
        answers=answers,
        form=form
    )
