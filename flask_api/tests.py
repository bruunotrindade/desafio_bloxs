from flask_unittest import ClientTestCase
from validate_docbr import CPF
import unittest

from app import create_app
from config import Config
from models import ContaModel

class TestConfig(object):
    TESTING = True

'''
    View de testes para a API
'''
class TestView(ClientTestCase):
    app = create_app(TestConfig)

    ''' 
       Teste de criação de pessoa
    '''
    def test_criar_pessoa(self, client):
        for i in range(5):
            info = {
                'nome': f"USUARIO {i}" , 
                'cpf': CPF().generate(), 
                'dataNascimento': '1984-05-10'
            }

            response = client.post(Config.PREFIX + "/pessoa/", data=info)
            self.assertInResponse(b"id", response)
            self.assertStatus(response, 201)

    ''' 
       Teste de criação de conta
    '''
    def test_criar_conta(self, client):
        for i in range(1, 5):
            info = {
                'limiteSaqueDiario': 5000.0,
                'tipoConta': 2,
                'idPessoa': i
            }

            response = client.post(Config.PREFIX + "/conta/", data=info)
            self.assertStatus(response, 201)

    ''' 
       Teste de depósito em conta
    '''
    def test_deposito_conta(self, client):
        with self.app.app_context():
            info = {
                'valor': 500.0
            }

            conta = ContaModel.query.filter_by(flagAtivo=True).first()
            if conta is not None:
                response = client.post(f"{Config.PREFIX}/conta/{conta.idConta}/deposito", data=info)
                self.assertInResponse(b'saldo', response)
                self.assertStatus(response, 200)

    ''' 
       Teste de saque em conta
    '''
    def test_saque_conta(self, client):
        with self.app.app_context():
            info = {
                'valor': 10.0
            }
            
            conta = ContaModel.query.filter(ContaModel.saldo >= 10).filter_by(flagAtivo=True).first()
            if conta is not None:
                response = client.post(f"{Config.PREFIX}/conta/{conta.idConta}/saque", data=info)
                self.assertInResponse(b'saldo', response)
                self.assertStatus(response, 200)

    ''' 
       Teste de saque em conta bloqueada
    '''
    def test_saque_conta_bloqueada(self, client):
        with self.app.app_context():
            info = {
                'valor': 10.0
            }
            
            conta = ContaModel.query.filter_by(flagAtivo=False).first()
            if conta is not None:
                response = client.post(f"{Config.PREFIX}/conta/{conta.idConta}/saque", data=info)
                self.assertStatus(response, 400)

    ''' 
       Teste de saque em conta sem saldo
    '''
    def test_saque_conta_sem_saldo(self, client):
        with self.app.app_context():
            info = {
                'valor': 10.0
            }
            
            conta = ContaModel.query.filter(ContaModel.saldo == 0).first()
            if conta is not None:
                response = client.post(f"{Config.PREFIX}/conta/{conta.idConta}/saque", data=info)
                self.assertStatus(response, 400)

    '''
        Teste de extrato de conta
    '''
    def test_extrato_conta(self, client):
        with self.app.app_context():
            id = ContaModel.query.first().idConta
            response = client.get(f"{Config.PREFIX}/conta/{id}/extrato")
            self.assertInResponse(b'extrato', response)
            self.assertStatus(response, 200)

    '''
        Teste de bloqueio em conta
    '''
    def test_bloqueio_conta(self, client):
        with self.app.app_context():
            conta = ContaModel.query.filter_by(flagAtivo=True).first()
            if conta is not None:
                response = client.post(f"{Config.PREFIX}/conta/{conta.idConta}/bloqueio")
                self.assertInResponse(b'sucesso', response)
                self.assertStatus(response, 200)

    '''
        Teste de desbloqueio de conta
    '''
    def test_desbloqueio_conta(self, client):
        with self.app.app_context():
            conta = ContaModel.query.filter_by(flagAtivo=False).first()
            if conta is not None:
                response = client.post(f"{Config.PREFIX}/conta/{conta.idConta}/desbloqueio")
                self.assertInResponse(b'sucesso', response)
                self.assertStatus(response, 200)

if __name__ == '__main__':
    unittest.main()