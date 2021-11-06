from flask_restful import Resource, reqparse, abort
from models import ContaModel, TransacaoModel
from config import db

class Conta(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('limiteSaqueDiario', type=float, required=True,
                        help='Campo obrigatório')
    parser.add_argument('tipoConta', type=int, required=True,
                        help='Campo obrigatório')
    parser.add_argument('idPessoa', type=int, required=True,
                        help='Campo obrigatório')

    def get(self):
        return {
            'contas': [conta.json() for conta in ContaModel.query.all()]} 

    def post(self):
        data = self.parser.parse_args()
        conta = ContaModel(data['limiteSaqueDiario'], data['tipoConta'], data['idPessoa'])

        try:
            conta.save()
        except:
            return {"message": "Falha ao salvar a conta"}, 500
            
        return conta.json(), 201


class ContaShow(Resource):
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            return conta.json()
        return {'message': 'Conta não encontrada'}, 404


class ContaSaldo(Resource):
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            return { "saldo": conta.saldo }
        return {'message': 'Conta não encontrada'}, 404

    
class ContaExtrato(Resource):
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            transacoes = [ transacao.json() for transacao in conta.get_transacoes() ]
            return { "extrato": transacoes }
        return {'message': 'Conta não encontrada'}, 404


class ContaDeposito(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('valor', type=float, required=True,
                        help='Campo obrigatório')

    def post(self, id):
        data = self.parser.parse_args()
        conta = ContaModel.find_by_id(id)

        if data['valor'] <= 0:
            abort(400, message="O valor deve ser positivo")
        elif conta is None:
            abort(404, message="Conta não encontrada")
        elif not conta.flagAtivo:
            abort(400, message="Esta conta está bloqueada")

        conta.saldo += data['valor']
        transacao = TransacaoModel(data['valor'], id)

        try:
            db.session.add(conta)
            db.session.add(transacao)
            db.session.commit()
        except:
            {'message': 'Falha ao executar operação'}, 500

        return conta.json()


class ContaSaque(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('valor', type=float, required=True,
                        help='Campo obrigatório')

    def post(self, id):
        data = self.parser.parse_args()
        conta = ContaModel.find_by_id(id)

        limite_disponivel = conta.get_limite_disponivel()

        if data['valor'] <= 0:
            abort(400, message="O valor deve ser positivo")
        elif conta is None:
            abort(404, message="Conta não encontrada")
        elif not conta.flagAtivo:
            abort(400, message="Esta conta está bloqueada")
        elif limite_disponivel <= 0:
            abort(400, message="O limite de saque diário foi excedido")
        elif data['valor'] > limite_disponivel:
            abort(400, message="O limite de saque diário disponível não permite o saque deste valor")
        elif conta.saldo < data['valor']:
            abort(400, message="Valor indisponível para o saque")

        conta.saldo -= data['valor']
        transacao = TransacaoModel(-data['valor'], id)

        try:
            db.session.add(conta)
            db.session.add(transacao)
            db.session.commit()
        except:
            {'message': 'Falha ao executar operação'}, 500

        return conta.json()

class ContaBloqueio(Resource):
    def post(self, id):
        conta = ContaModel.find_by_id(id)

        if conta is None:
            abort(404, message="Conta não encontrada")
        elif not conta.flagAtivo:
            abort(400, message="Conta já foi bloqueada")

        conta.flagAtivo = False
        try:
            conta.save()
        except:
            return {"message": "Falha ao salvar a conta"}, 500

        return {'message': 'Conta bloqueada com sucesso'}, 200