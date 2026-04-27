import psycopg2
import os
from dotenv import load_dotenv
import datetime 
load_dotenv()

DB_CONF = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"), 
    "host": os.getenv("DB_HOST"),
    "port": "5432"
}

def cadastrar_produto(nome, validade, qtd):
    try:
        # Conecta ao banco
        conn = psycopg2.connect(**DB_CONF)
        cursor = conn.cursor()

        # SQL para inserção
        query = """
            INSERT INTO produtos (nome, data_validade, quantidade, status_ia)
            VALUES (%s, %s, %s, %s)
        """
        
        
        # Se falta menos de 30 dias, a "IA" marca como Alerta
        hoje = datetime.datetime.now()
        data_val = datetime.datetime.strptime(validade, "%Y-%m-%d")
        dias_restantes = (data_val - hoje).days
        
        status = "Seguro" if dias_restantes > 5 else "Alerta Crítico"

        
        cursor.execute(query, (nome, validade, qtd, status))
        
        conn.commit()
        print(f"✅ Sucesso! {nome} cadastrado com status: {status}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

# Testando a inserção
if __name__ == "__main__":
    cadastrar_produto("Leite Integral", "2026-05-10", 12)
    cadastrar_produto("Iogurte Grego", "2026-04-28", 5)