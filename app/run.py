from flask import Flask
from flask_restful import Api

from config import MySQLConfig

from resources import ContaShow, ContaSaldo, Conta, ContaDeposito, ContaSaque, ContaExtrato, ContaBloqueio

app = Flask(__name__)
app.config.from_object(MySQLConfig)

api = Api(app)

@app.before_first_request
def create_tables():
    from config import db
    
    db.init_app(app)
    db.create_all()


api.add_resource(Conta, '/conta/')
api.add_resource(ContaShow, '/conta/<int:id>')
api.add_resource(ContaSaldo, '/conta/<int:id>/saldo')
api.add_resource(ContaDeposito, '/conta/<int:id>/deposito')
api.add_resource(ContaBloqueio, '/conta/<int:id>/bloqueio')
api.add_resource(ContaSaque, '/conta/<int:id>/saque')
api.add_resource(ContaExtrato, '/conta/<int:id>/extrato')

if __name__ == '__main__':
    app.run(debug=True)