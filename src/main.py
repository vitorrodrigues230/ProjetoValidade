from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import date
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que qualquer origem (como sua porta 5500) acesse a API
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, PUT, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

@app.get("/api/inventario")
def get_inventario():
    conn = get_db_connection()
    # O RealDictCursor permite acessar as colunas pelo nome: r['produto']
    cur = conn.cursor(cursor_factory=RealDictCursor) 
    
    try:
        # Verifique se os nomes das colunas (id_externo, status_ia) estão corretos no seu banco
        cur.execute("""
            SELECT id_externo,nome as produto, categoria, data_validade, quantidade as qtd, status_ia as status FROM produtos""")
        
        dados = cur.fetchall()
        
        inventario = []
        for r in dados:
        
            data_formatada = "---"
            if r.get('data_validade'):
                data_formatada = r['data_validade'].strftime('%d/%m/%Y')
            inventario.append({
            "id_externo": r['id_externo'],
            "produto": r['produto'],
            "categoria": r['categoria'],
            "validade": data_formatada,
            "qtd": r['qtd'],    
            "status": r['status'] 
            })
            
        return inventario
    except Exception as e:
        print(f"Erro detalhado no console: {e}")
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()
@app.post("/api/sincronizar")
def sincronizar_estoque():
    conn = get_db_connection()
    cur = conn.cursor()

    # Simulação: Estes dados viriam de uma SELECT no banco do cliente
    dados_cliente = [
        {"id_externo": 101, "nome": "Leite Integral 1L", "categoria": "Laticínios"},
        {"id_externo": 102, "nome": "Iogurte Natural", "categoria": "Laticínios"},
        {"id_externo": 103, "nome": "Arroz 5kg", "categoria": "Grãos"},
        {"id_externo": 104, "nome": "Feijão Carioca 1kg", "categoria": "Grãos"}, # NOVO ITEM
        {"id_externo": 105, "nome": "Suco de Laranja 1L", "categoria": "Bebidas"}  # NOVO ITEM
    ]

    produtos_adicionados = 0

    for item in dados_cliente:
        # O comando ON CONFLICT garante que não vamos duplicar o produto se o id_externo já existir
        cur.execute("""
            INSERT INTO produtos (id_externo, nome, categoria, status_ia)
            VALUES (%s, %s, %s, 'Sem Validade')
            ON CONFLICT (id_externo) DO NOTHING;
        """, (item['id_externo'], item['nome'], item['categoria']))
        
        if cur.rowcount > 0:
            produtos_adicionados += 1

    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "sucesso", 
        "novos_itens": produtos_adicionados,
        "mensagem": f"Sincronização concluída. {produtos_adicionados} novos itens encontrados."
    }

class DadosVinculo(BaseModel):
    id_externo: int
    data_validade: str 

@app.put("/api/vincular-validade")
async def vincular_validade(payload: dict):
    id_ext = payload.get("id_externo")
    data_val = payload.get("data_validade")
    
    print(f"Tentando atualizar ID Externo: {id_ext} com Data: {data_val}") # Debug no terminal

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE produtos 
            SET data_validade = %s, status_ia = 'Seguro'
            WHERE id_externo = %s
        """, (data_val, id_ext))
        
        # Verifica quantas linhas foram alteradas
        linhas_afetadas = cur.rowcount
        print(f"Linhas afetadas no banco: {linhas_afetadas}")

        conn.commit() # Garante que a alteração seja salva
        
        if linhas_afetadas == 0:
            return {"status": "erro", "mensagem": "Produto não encontrado no banco."}
            
        return {"status": "sucesso"}
    except Exception as e:
        conn.rollback()
        print(f"Erro no banco: {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        cur.close()
        conn.close()