import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '33lkjdf#897lk'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
