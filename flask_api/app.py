from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from config import Config, db
from resources import Pessoa, ContaShow, ContaSaldo, Conta, ContaDeposito, ContaSaque, ContaExtrato, ContaBloqueio, ContaDesbloqueio

'''
    Método para criar App e retorná-la
'''
def create_app(test=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test is not None:
        app.config.from_object(test)
        db.init_app(app)

    api = Api(app, prefix=Config.PREFIX)

    swagger = Swagger(app)

    @app.before_first_request
    def create_tables():
        db.init_app(app)
        db.create_all()

    # Rotas disponíveis na API
    api.add_resource(Pessoa, '/pessoa/')
    api.add_resource(Conta, '/conta/')
    api.add_resource(ContaShow, '/conta/<int:id>')
    api.add_resource(ContaSaldo, '/conta/<int:id>/saldo')
    api.add_resource(ContaDeposito, '/conta/<int:id>/deposito')
    api.add_resource(ContaBloqueio, '/conta/<int:id>/bloqueio')
    api.add_resource(ContaDesbloqueio, '/conta/<int:id>/desbloqueio')
    api.add_resource(ContaSaque, '/conta/<int:id>/saque')
    api.add_resource(ContaExtrato, '/conta/<int:id>/extrato')

    '''
        Documentação disponibilizada via Swagger
        Endpoint: /apidocs/
    '''
    return app

if __name__ == '__main__':
    create_app().run(debug=True)