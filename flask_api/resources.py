from flask_restful import Resource, reqparse, abort, inputs
from flasgger import swag_from
from re import sub
from validate_docbr import CPF
from models import ContaModel, PessoaModel, TransacaoModel
from config import db

'''
    Resource para o endpoint /pessoa/ para as operações:
    - [GET] listar todas as pessoas
    - [POST] cadastrar uma pessoa
'''
class Pessoa(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('nome', type=str, required=True, 
                        help='Campo obrigatório')
    parser.add_argument('cpf', type=str, required=True,
                        help='Campo obrigatório')
    parser.add_argument('dataNascimento', type=inputs.date, required=True,
                        help='Campo obrigatório')

    @swag_from("docs/pessoa_get.yml")
    def get(self):
        return {
            'pessoas': [pessoa.json() for pessoa in PessoaModel.query.all()]} 

    @swag_from("docs/pessoa_post.yml")
    def post(self):
        data = self.parser.parse_args()


        data['cpf'] = sub('[^0-9]', '', data['cpf'])

        if not CPF().validate(data['cpf']):
            abort(400, message="CPF inválido")
        elif PessoaModel.find_by_cpf(data['cpf']):
            abort(400, message="CPF já cadastrado")

        pessoa = PessoaModel(data['nome'], data['cpf'], data['dataNascimento'])

        try:
            pessoa.save()
        except:
            return {"message": "Falha ao salvar a pessoa"}, 500
            
        return pessoa.json(), 201

'''
    Resource para o endpoint /conta/ para as operações:
    - [GET] listar todas as contas
    - [POST] criar uma conta
'''
class Conta(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('limiteSaqueDiario', type=float, required=True,
                        help='Campo obrigatório')
    parser.add_argument('tipoConta', type=int, required=True,
                        help='Campo obrigatório')
    parser.add_argument('idPessoa', type=int, required=True,
                        help='Campo obrigatório')

    @swag_from("docs/conta_get.yml")
    def get(self):
        return {
            'contas': [conta.json() for conta in ContaModel.query.all()]} 

    @swag_from("docs/conta_post.yml")
    def post(self):
        data = self.parser.parse_args()
        conta = ContaModel(data['limiteSaqueDiario'], data['tipoConta'], data['idPessoa'])

        try:
            conta.save()
        except:
            return {"message": "Falha ao salvar a conta"}, 500
            
        return conta.json(), 201

'''
    Resource para o endpoint /conta/{id} para a operação de mostrar uma conta
'''
class ContaShow(Resource):
    @swag_from("docs/conta_show.yml")
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            return conta.json()
        return {'message': 'Conta não encontrada'}, 404

'''
    Resource para o endpoint /conta/{id}/saldo para mostrar o saldo de uma conta
'''
class ContaSaldo(Resource):
    @swag_from("docs/conta_saldo.yml")
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            return { "saldo": conta.saldo }
        return {'message': 'Conta não encontrada'}, 404

'''
    Resource para o endpoint /conta/{id}/extrato para mostrar as operações de uma conta
'''
class ContaExtrato(Resource):
    @swag_from("docs/conta_extrato.yml")
    def get(self, id):
        conta = ContaModel.find_by_id(id)
        if conta:
            transacoes = [ transacao.json() for transacao in conta.get_transacoes() ]
            return { "extrato": transacoes }
        return {'message': 'Conta não encontrada'}, 404

'''
    Resource para o endpoint /conta/{id}/deposito para depositar em uma conta
'''
class ContaDeposito(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('valor', type=float, required=True,
                        help='Campo obrigatório')

    @swag_from("docs/conta_deposito.yml")
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

'''
    Resource para o endpoint /conta/{id}/saque para sacar dee uma conta
'''
class ContaSaque(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('valor', type=float, required=True,
                        help='Campo obrigatório')

    @swag_from("docs/conta_saque.yml")
    def post(self, id):
        data = self.parser.parse_args()
        conta = ContaModel.find_by_id(id)

        if conta is None:
            abort(404, message="Conta não encontrada")

        limite_disponivel = conta.get_limite_disponivel()

        if data['valor'] <= 0:
            abort(400, message="O valor deve ser positivo")
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

'''
    Resource para o endpoint /conta/{id}/bloqueio para bloquear uma conta
'''
class ContaBloqueio(Resource):
    @swag_from("docs/conta_bloqueio.yml")
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

'''
    Resource para o endpoint /conta/{id}/desbloqueio para desbloquear uma conta
'''
class ContaDesbloqueio(Resource):
    @swag_from("docs/conta_desbloqueio.yml")
    def post(self, id):
        conta = ContaModel.find_by_id(id)

        if conta is None:
            abort(404, message="Conta não encontrada")
        elif conta.flagAtivo:
            abort(400, message="Conta já foi desbloqueada")

        conta.flagAtivo = True
        try:
            conta.save()
        except:
            return {"message": "Falha ao salvar a conta"}, 500

        return {'message': 'Conta desbloqueada com sucesso'}, 200