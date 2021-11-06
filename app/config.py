from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values

env = dotenv_values(".env")

MYSQL_HOST = env.get("MYSQL_HOST")
MYSQL_USER = env.get("MYSQL_USER")
MYSQL_PWD = env.get("MYSQL_PASSWORD")
MYSQL_DB = env.get("MYSQL_DATABASE")

mysql_uri = f"mysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}/{MYSQL_DB}"


class MySQLConfig(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = mysql_uri


db = SQLAlchemy()