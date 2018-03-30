import os

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@opsrv.mapout.lan:3306/demo'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass

config = {
    'develop_config': Config
}
