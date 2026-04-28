from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    cur = conn.cursor()
    

    cur.execute("SELECT nome, categoria, data_validade, quantidade, status_ia FROM produtos")
    rows = cur.fetchall()
    
    inventario = []
    for r in rows:
        inventario.append({
            "produto": r[0],
            "categoria": r[1],
            "validade": r[2].strftime('%d/%m/%Y') if r[2] else "---",
            "qtd": r[3],
            "status": r[4]
        })
    
    cur.close()
    conn.close()
    return inventario