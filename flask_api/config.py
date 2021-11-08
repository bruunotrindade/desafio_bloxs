from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values

# Extraindo configurações do arquivo .env
env = dotenv_values(".env")

MYSQL_HOST = env.get("MYSQL_HOST")
MYSQL_USER = env.get("MYSQL_USER")
MYSQL_PWD = env.get("MYSQL_PASSWORD")
MYSQL_DB = env.get("MYSQL_DATABASE")
MYSQL_URI = f"mysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}/{MYSQL_DB}"

# Configurações de ambiente de desenvolvimento
class Config(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = MYSQL_URI
    PREFIX = "/api/v1"
    SWAGGER = {
        'title': 'Desafio Bloxs',
        'description': 'Desenvolvido por Bruno Trindade',
        'termsOfService': None,
        'version': '1.0'
    }

db = SQLAlchemy()