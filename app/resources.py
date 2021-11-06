from flask_restful import Resource, reqparse, abort
from models import ContaModel, TransacaoModel


class Conta(Resource):
    parser = reqparse.RequestParser()  # only allow price changes, no name changes allowed

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
            return {"message": "An error occurred inserting the item."}, 500
            
        return conta.json(), 201


class ContaShow(Resource):
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            return conta.json()
        return {'message': 'Conta não encontrada.'}, 404


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

        conta.saldo += data['valor']
        conta.save()

        transacao = TransacaoModel(data['valor'], id)
        transacao.save()

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
        elif limite_disponivel <= 0:
            abort(400, message="O limite de saque diário foi excedido")
        elif data['valor'] > limite_disponivel:
            abort(400, message="O limite de saque diário disponível não permite o saque deste valor")
        elif conta.saldo < data['valor']:
            abort(400, message="Saldo indisponível para o saque")

        conta.saldo -= data['valor']
        conta.save()

        transacao = TransacaoModel(-data['valor'], id)
        transacao.save()

        return conta.json()