import pandas as pd
import nltk
from nltk.stem import SnowballStemmer
import spacy

# fazer relatorio entre diferença stem e lema para representante de palavras

def teste_representante():
    caminho = r"C:\Users\Windows 11\Documents\ShinyPy_MineracaoTextos\ShinyPy_MineracaoTextos\TESTES\dados_processados_20251117_224012.csv"

    dados_processados = pd.read_csv(caminho, encoding='utf-8')
    
    print("Primeiras 5 linhas:")
    print(dados_processados.head(5))
            
    coluna_texto = None
    for coluna in dados_processados.columns:
        if dados_processados[coluna].dtype == 'object':
            coluna_texto = coluna
            break

    print(f"\nNome coluna de texto: '{coluna_texto}'")

    # FREQUENCIA ABSOLUTA
    dados_freq = (
        dados_processados[coluna_texto]
        .dropna()
        .astype(str)
        .str.split()
        .explode()
        .str.lower()
        .value_counts()
        .reset_index()
    )

    dados_freq.columns = ['Palavra', 'Frequência']
    dados_freq = dados_freq.sort_values(by='Frequência', ascending=False).reset_index(drop=True)
    
    print(f"\n{len(dados_freq)} palavras únicas")
    print("\n10 PALAVRAS MAIS FREQUENTES:")
    print(dados_freq.head(10).to_string(index=False))
    
    '''
    # REPRESENTANTE POR STEMMING
    stemmer = SnowballStemmer('portuguese')
    palavras_originais = []
    stems = []

    for index, row in dados_freq.iterrows():
        palavra = row['Palavra']
        frequencia = row['Frequência']
        stem = stemmer.stem(palavra)

        if stem not in stems:
            palavras_originais.append(palavra)
            stems.append(stem)

    resultadoStem = pd.DataFrame({
        "Palavra_Representante": palavras_originais,
        "Stem_Agrupador": stems
    })

    print(f"\n{len(resultadoStem)} stems únicos")
    print("\nPRIMEIROS 15 REPRESENTANTES STEM:")
    print(resultadoStem.head(15).to_string(index=False))

    '''

    # REPRESENTANTE POR LEMATIZAÇÃO USANDO NLTK
        # Não funciona pq o nltk não tem suporte para lematização em português
    
    # REPRESENTANTE POR LEMATIZAÇÃO USANDO SPACY
    # criar dicionario de atrativos turísticos do paraná para melhorar lematização, substituir areiar por areia
    # colocar parametrização: processo de seleção das palavras que não devem ser processadas pelo código, lembrar stopwords. O usuário escolhe
    nlp = spacy.load("pt_core_news_sm")
    palavras_representantes = []
    lemas_agrupadores = []

    for _, row in dados_freq.iterrows():
        palavra = row['Palavra']
        doc = nlp(palavra)
        
        if len(doc) > 0:
            token = doc[0]
            if token.pos_ in ["VERB", "AUX"]:
                lemma = token.lemma_.lower()
            else:
                lemma = palavra.lower()  

            if lemma not in lemas_agrupadores:
                palavras_representantes.append(palavra)
                lemas_agrupadores.append(lemma)

    resultadoLema = pd.DataFrame({
        "Palavra_Representante": palavras_representantes,
        "Lema_Agrupador": lemas_agrupadores
    })

    print(f"\n{len(resultadoLema)} lemas únicos")
    print("\nPRIMEIROS 15 REPRESENTANTES LEMA:")
    print(resultadoLema.head(15).to_string(index=False))

    # COMPARATIVO
    # Renomear colunas para facilitar merge
    freq = dados_freq.rename(columns={"Palavra": "Palavra_Original"})
    #stem = resultadoStem.rename(columns={"Palavra_Representante": "Palavra_Original"})
    lema = resultadoLema.rename(columns={"Palavra_Representante": "Palavra_Original"})

    # Fazer merge progressivo
    #comparativo = freq.merge(stem, on="Palavra_Original", how="left") \ .merge(lema, on="Palavra_Original", how="left")
    comparativo = freq.merge(lema, on="Palavra_Original", how="left")

    print("\n=== COMPARAÇÃO: Palavra | Frequência | Stem | Lemma ===")
    print(comparativo.head(30).to_string(index=False))

    return comparativo

if __name__ == "__main__":
    resultado = teste_representante()
