import pandas as pd
from nltk.stem import SnowballStemmer
import spacy


def teste_representante():
    caminho = r"Input\00_ComentariosSuperagui.csv"

    # leitura robusta
    try:
        dados_processados = pd.read_csv(caminho, encoding='utf-8', sep=';')
    except Exception:
        dados_processados = pd.read_csv(caminho, encoding='utf-8', sep=None, engine='python')

    print("Primeiras 5 linhas:")
    print(dados_processados.head(5))

    # coluna fixa
    coluna_texto = "coments"
    if coluna_texto not in dados_processados.columns:
        raise ValueError(f"A coluna '{coluna_texto}' não existe no dataset.")

    # =========================
    # FREQUÊNCIA
    # =========================
    dados_freq = (
        dados_processados[coluna_texto]
        .dropna()
        .astype(str)
        .str.lower()
        .str.split()
        .explode()
        .value_counts()
        .reset_index()
    )

    dados_freq.columns = ['Palavra', 'Frequência']
    dados_freq = dados_freq.sort_values(by='Frequência', ascending=False).reset_index(drop=True)

    print(f"\n{len(dados_freq)} palavras únicas")

    # =========================
    # STEM (TODAS as palavras)
    # =========================
    stemmer = SnowballStemmer('portuguese')
    dados_freq['Stem'] = dados_freq['Palavra'].apply(stemmer.stem)

    # =========================
    # LEMMA (TODAS as palavras)
    # =========================
    nlp = spacy.load("pt_core_news_md")

    docs = list(nlp.pipe(dados_freq['Palavra']))

    lemas = []

    for doc, palavra in zip(docs, dados_freq['Palavra']):
        if len(doc) == 0:
            lemas.append(palavra)
            continue

        token = doc[0]
        lemma = token.lemma_.lower()

        if lemma not in palavra:
            lemma = palavra

        lemas.append(lemma)

    dados_freq['Lemma'] = lemas

    # =========================
    # REPRESENTANTES STEM
    # =========================
    resultadoStem = (
        dados_freq
        .drop_duplicates(subset=['Stem'])
        [['Palavra', 'Stem']]
        .rename(columns={
            "Palavra": "Palavra_Representante",
            "Stem": "Stem_Agrupador"
        })
    )

    print(f"\n{len(resultadoStem)} stems únicos")
    print("\nPRIMEIROS 50 REPRESENTANTES STEM:")
    print(resultadoStem.head(50).to_string(index=False))

    # =========================
    # REPRESENTANTES LEMA
    # =========================
    resultadoLema = (
        dados_freq
        .drop_duplicates(subset=['Lemma'])
        [['Palavra', 'Lemma']]
        .rename(columns={
            "Palavra": "Palavra_Representante",
            "Lemma": "Lema_Agrupador"
        })
    )

    print(f"\n{len(resultadoLema)} lemas únicos")
    print("\nPRIMEIROS 50 REPRESENTANTES LEMA:")
    print(resultadoLema.head(50).to_string(index=False))

    # =========================
    # COMPARATIVO (SEM MERGE)
    # =========================
    print("\n=== COMPARAÇÃO: Palavra | Frequência | Stem | Lemma ===")
    print(dados_freq.head(150).to_string(index=False))

    return dados_freq


if __name__ == "__main__":
    resultado = teste_representante()

    resultado.to_excel("resultado_frequencia.xlsx", index=False)