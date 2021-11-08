# Desafio Bloxs

   O problema consiste em um sistema bancário com criação de pessoas físicas, contas bancárias e as operações de saque, depósito, extrato e bloqueio. A solução foi com Flask-RESTful, SQLAlchemy, MySQL e com documentação por Swagger (Flasgger).

# Execução com Docker-Compose

1. Possuir o docker-compose instalado e configurado na máquina;

2. Criar arquivo **.env** a partir de **.env.example**. PS: Caso utilizado banco externo, as credenciais de acesso do arquivo **.env** devem ser alteradas;

3. Utilizar o comando de inicialização dos containers:

```
docker-compose up --build
```

4. Por padrão, a API é disponibilizada em localhost na porta 5000. Por exemplo: http://localhost:5000/


# Documentação

A documentação está disponível no endpoint **/apidocs/** e, para acessá-la, a API deve estar em execução. Caso seja utilizado o docker-compose nas configurações disponibilizadas, por exemplo, a mesma poderá ser acessada através de http://localhost:5000/apidocs/. 
