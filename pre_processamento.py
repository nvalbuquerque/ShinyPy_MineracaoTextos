from shiny import render, output
import pandas as pd
import string
from logica import processa_dados

def remove_pontuacao_numeros(df):
    if isinstance(df, pd.DataFrame):
        df_limpo = df.copy()
        for coluna in df_limpo.columns:
            if df_limpo[coluna].dtype == 'object':  # Colunas de texto
                df_limpo[coluna] = df_limpo[coluna].str.translate(
                    str.maketrans('', '', string.punctuation)
                )
                return df_limpo
            else:
                return df
            
@output
@render.table
def tabela_sem_pontuacao():  
    dados = processa_dados()
    if isinstance(dados, pd.DataFrame):
        return remove_pontuacao_numeros(dados)  
    return dados

