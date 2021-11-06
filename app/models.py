from config import db
from datetime import datetime, timedelta
from sqlalchemy.sql import func

class BasicMixin(object):
    def save(self):
        db.session.add(self)
        db.session.commit() 

    def delete(self):
        db.session.delete(self)
        db.session.commit() 


class PessoaModel(BasicMixin, db.Model):
    __tablename__ = 'pessoa'

    idPessoa = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(180), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    dataNascimento = db.Column(db.Date, nullable=False)

    def __init__(self, nome, cpf, dataNascimento):
        self.nome = nome
        self.cpf = cpf
        self.dataNascimento = dataNascimento

    def json(self):
        return {'nome': self.nome, 'cpf': self.cpf, 'dataNascimento': self.dataNascimento}

    @classmethod
    def find_by_name(cls, nome):
        return cls.query.filter_by(nome=nome).first()


class ContaModel(BasicMixin, db.Model):
    class TipoConta:
        CORRENTE = 1
        POUPANCA = 2

    __tablename__ = 'conta'

    idConta = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Float(precision=2), default=0.0, nullable=False)
    limiteSaqueDiario = db.Column(db.Float(precision=2), nullable=False)
    flagAtivo = db.Column(db.Boolean, default=True, nullable=False)
    tipoConta = db.Column(db.Integer, default=TipoConta.CORRENTE, nullable=False)
    dataCriacao = db.Column(db.DateTime(), default=datetime.now(), nullable=False)

    idPessoa = db.Column(db.Integer, db.ForeignKey('pessoa.idPessoa'), nullable=False)
    pessoa = db.relationship('PessoaModel')

    def __init__(self, limiteSaqueDiario, tipoConta, idPessoa):
        self.limiteSaqueDiario = limiteSaqueDiario
        self.tipoConta = tipoConta
        self.idPessoa = idPessoa

    def json(self):
        return {'saldo': self.saldo, 'limiteSaqueDiario': self.limiteSaqueDiario, 'flagAtivo': self.flagAtivo, 'tipoConta': self.tipoConta}

    def get_limite_disponivel(self):
        date = datetime.now().date()
        id = self.idConta
        limiteUsado = db.session.query(func.sum(TransacaoModel.valor)).filter(db.and_(TransacaoModel.idConta == id, TransacaoModel.valor < 0,
            TransacaoModel.dataTransacao.between(date, date + timedelta(days=1)))).first()[0]

        if limiteUsado is None:
            return self.limiteSaqueDiario

        return self.limiteSaqueDiario - abs(limiteUsado)

    def get_transacoes(self):
        return TransacaoModel.query.filter_by(idConta=self.idConta).all()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(idConta=id).first()


class TransacaoModel(BasicMixin, db.Model):
    __tablename__ = 'transacao'

    idTransacao = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float(precision=2), default=0.0, nullable=False)
    dataTransacao = db.Column(db.DateTime(), default=datetime.now(), nullable=False)

    idConta = db.Column(db.Integer, db.ForeignKey('conta.idConta'), nullable=False)
    conta = db.relationship('ContaModel')

    def __init__(self, valor, idConta):
        self.valor = valor
        self.idConta = idConta

    def json(self):
        return {'valor': self.valor, 'dataTransacao': str(self.dataTransacao)}