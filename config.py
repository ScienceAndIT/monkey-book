import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'try to guess this secret key!'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MONKEYS_PER_PAGE = 4
    FOLLOWERS_PER_PAGE = 5

    # e-mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MONKEYBOOK_MAIL_SUBJECT_PREFIX = '[MonkeyBook]'
    MONKEYBOOK_MAIL_SENDER = os.environ.get('MONKEYBOOK_MAIL_SENDER')
    MONKEYBOOK_ADMIN = os.environ.get('MONKEYBOOK_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}