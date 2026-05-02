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
    hoje = date.today()
    try:
        # Verifique se os nomes das colunas (id_externo, status_ia) estão corretos no seu banco
        cur.execute("""
            SELECT id_externo,nome as produto, categoria, data_validade, quantidade as qtd, status_ia as status FROM produtos""")
        
        dados = cur.fetchall()
        
        inventario = []
        for r in dados:
            validade = r['data_validade']
            status_calculado = "Seguro"
            data_formatada = "---"
            if validade:
                data_formatada = validade.strftime('%d/%m/%Y')
                # Calculamos a diferença em dias
                dias_restantes = (validade - hoje).days

                # Lógica de Automação
                if dias_restantes < 0:
                    status_calculado = "Crítico"  # Vencido entra como Crítico no seu CSS
                elif dias_restantes <= 7:
                    status_calculado = "Crítico"
                elif dias_restantes <= 15:
                    status_calculado = "Atenção"
                else:
                    status_calculado = "Seguro"

            inventario.append({
                "id_externo": r['id_externo'],
                "produto": r['produto'],
                "categoria": r['categoria'],
                "validade": data_formatada,
                "qtd": r['qtd'],
                "status": status_calculado  # Agora o status é dinâmico!
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
@app.get("/api/vencimentos_proximos")
def get_vencimentos_proximos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    hoje = date.today()
    
    try:
        # Buscamos os 5 que vencem primeiro (que não venceram há muito tempo)
        cur.execute("""
            SELECT nome as produto, data_validade
            FROM produtos
            WHERE data_validade IS NOT NULL
            ORDER BY data_validade ASC
            LIMIT 5
        """)
        
        dados = cur.fetchall()
        top_vencimentos = []

        for r in dados:
            dias = (r['data_validade'] - hoje).days
            
            # Formatação do texto do badge (ex: "3 dias" ou "Vencido")
            texto_dias = f"{dias} dias" if dias >= 0 else "Vencido"
            
            # Define a cor do badge com base na urgência
            cor_badge = "badge-critico" if dias <= 7 else "badge-alerta"

            top_vencimentos.append({
                "produto": r['produto'],
                "dias_texto": texto_dias,
                "classe_cor": cor_badge
            })
            
        return top_vencimentos
    finally:
        cur.close()
        conn.close()