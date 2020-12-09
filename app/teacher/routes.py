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
from app.teacher import bp

@bp.route('/teacher')
def index():
    return render_template('teacher/index.html', title='Home')
