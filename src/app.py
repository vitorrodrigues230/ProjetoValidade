import streamlit as st
import pandas as pd
import plotly.express as px  
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv


st.set_page_config(page_title="Gestor Pro IA", page_icon="📦", layout="wide")

load_dotenv()


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port="5432"
    )


st.title("📦 Gestor de Validade Inteligente")
st.markdown("Monitoramento em tempo real para redução de desperdício.")


try:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM produtos ORDER BY data_validade ASC", conn)
    conn.close()
except Exception as e:
    st.error(f"Erro de conexão: {e}")
    df = pd.DataFrame()


if not df.empty:
    total_itens = len(df)
    em_alerta = len(df[df['status_ia'] == 'Alerta Crítico'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Itens", total_itens)
    m2.metric("Em Alerta", em_alerta, delta=em_alerta, delta_color="inverse")
    m3.metric("Status do Sistema", "Online", delta="Ativo")

st.markdown("---")


col_form, col_visual = st.columns([1, 2])

with col_form:
    st.subheader("➕ Novo Cadastro")
    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome do Produto", placeholder="Ex: Leite Integral")
        validade = st.date_input("Data de Validade")
        quantidade = st.number_input("Quantidade em Estoque", min_value=1)
        
        btn_salvar = st.form_submit_button("Cadastrar no Banco")

    if btn_salvar and nome:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            dias = (validade - datetime.now().date()).days
            status = "Seguro" if dias > 30 else "Alerta Crítico"
            
            query = "INSERT INTO produtos (nome, data_validade, quantidade, status_ia) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nome, validade, quantidade, status))
            conn.commit()
            st.success(f"Sucesso: {nome} adicionado!")
            st.rerun() # Atualiza a página para mostrar o novo item
        except Exception as e:
            st.error(f"Erro: {e}")

with col_visual:
    st.subheader("📊 Monitoramento de Estoque")
    
    if not df.empty:
    
        def color_status(val):
            color = '#ff4b4b' if val == 'Alerta Crítico' else '#28a745'
            return f'color: {color}; font-weight: bold'

        # Tabela estilizada
        st.dataframe(
            df[['nome', 'data_validade', 'quantidade', 'status_ia']].style.map(color_status, subset=['status_ia']),
            use_container_width=True
        )
        
        
        st.markdown("### Visão Geral de Riscos")
        fig = px.pie(df, names='status_ia', hole=0.4, 
                     color='status_ia',
                     color_discrete_map={'Seguro':'#28a745', 'Alerta Crítico':'#ff4b4b'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aguardando o primeiro cadastro para gerar relatórios.")