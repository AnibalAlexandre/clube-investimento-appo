import streamlit as st
import pandas as pd

st.title("Clube de Investimento APPO")
st.subheader("Painel de Gestão e Controlo")

# Exemplo de conteúdo para o seu clube:
st.write("Bem-vindo à plataforma de gestão do clube.")

# Pode adicionar tabelas ou dados aqui
dados = {
    "Membro": ["Sócio A", "Sócio B", "Sócio C"],
    "Quota (Kz)": [50000, 75000, 60000]
}
df = pd.DataFrame(dados)
st.dataframe(df)
