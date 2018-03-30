from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flask_restful import current_app

# postgres_engine = create_engine('postgresql://postgres:postgres@192.168.10.6:5432/cof')
# db_session = sessionmaker(bind=postgres_engine)
# session = db_session()

engine_mysql = create_engine('mysql+pymysql://root:root@opsrv.mapout.lan:3306/demo?charset=utf8')
db_session = sessionmaker(bind=engine_mysql)
session = db_session()

