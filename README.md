Gestor de Validade Inteligente 🚀
Este projeto é um sistema de monitoramento de validade de produtos que utiliza Python e PostgreSQL. O objetivo é fornecer uma gestão automatizada de estoques, utilizando lógica de programação para classificar o status de criticidade dos produtos com base na proximidade da data de vencimento.

🛠️ Tecnologias Utilizadas
Linguagem: Python 3.x
Banco de Dados: PostgreSQL
Segurança: Variáveis de Ambiente (python-dotenv)
Conectividade: Psycopg2 (Driver PostgreSQL para Python)
Versionamento: Git & GitHub

📋 Funcionalidades Atuais
[x] Configuração de ambiente isolado com venv.

[x] Conexão segura entre Python e PostgreSQL via variáveis de ambiente.

[x] Criação automatizada de banco de dados e tabelas.

[x] Script de inserção de produtos com cálculo automático de status (Seguro/Alerta).

🚀 Como Executar o Projeto
1. Pré-requisitos
Certifique-se de ter o Python e o PostgreSQL instalados em sua máquina.

2. Configuração do Banco de Dados
Crie um banco de dados chamado gestor_validade_ia e execute o comando SQL abaixo para criar a tabela principal:

SQL
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_validade DATE NOT NULL,
    quantidade INT DEFAULT 1,
    status_ia VARCHAR(50)
);
3. Instalação
Clone o repositório e instale as dependências necessárias:

Bash
git clone https://github.com/vitorrodrigues230/ProjetoValidade.git
cd ProjetoValidade
pip install -r requirements.txt

4. Configuração das Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto (utilize o .env.example como base) e insira suas credenciais:

Plaintext
DB_NAME=gestor_validade_ia
DB_USER=seu_usuario_postgres
DB_PASSWORD=sua_senha_secreta
DB_HOST=localhost

5. Executando o Script
Para realizar a inserção de teste e validar a conexão com o banco de dados, execute:

Bash
python src/main.py


🛡️ Segurança
O projeto segue boas práticas de segurança, utilizando um arquivo .gitignore para garantir que o ambiente virtual (venv) e as credenciais sensíveis (.env) não sejam enviados para o repositório público.

Desenvolvido por Vitor Rodrigues Ferreira