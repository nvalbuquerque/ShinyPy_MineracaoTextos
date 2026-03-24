from shiny import reactive, render, ui
import pandas as pd
from config import load_stopwords
import spacy
import re
# Biblioteca média de língua portuguesa no spaCy
nlp = spacy.load("pt_core_news_md")
from nltk.stem import SnowballStemmer 
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import unicodedata

stopwords_data = load_stopwords()
stopwords_ptBR = stopwords_data['stopwords_ptBR']
stopwords_comentarios = stopwords_data['stopwords_comentarios']
stopwords_iso = stopwords_data['stopwords_iso']
all_stopwords = stopwords_data['all_stopwords']

def setup_server(input, output, session): 
    @reactive.Calc  
    def processa_dados():
        file_info = input.file1()
        if file_info is None:
            return None
        
        file = file_info[0]
        caminho = file['datapath']
        
        try: 
            if file['name'].endswith('.csv') or file['name'].endswith('.txt'):
                df = None
                for encoding in ['utf-8']:
                    try:
                        with open(caminho, 'r', encoding=encoding) as f:
                            primeira_linha = f.readline().strip()
                        
                        if not primeira_linha:
                            continue
                        
                        separadores = [';', ',', '\t']
                        separador = max(separadores, key=lambda x: primeira_linha.count(x))
                        
                        if primeira_linha.count(separador) == 0:
                            with open(caminho, 'r', encoding=encoding) as f:
                                linhas = []
                                for linha in f:
                                    linha_limpa = linha.strip()
                                    if linha_limpa:  
                                        linhas.append(linha_limpa)
                            
                            if linhas:
                                df = pd.DataFrame({'conteudo': linhas})
                            else:
                                df = pd.DataFrame({'conteudo': ['Arquivo vazio']})
                        
                        else:
                            df = pd.read_csv(
                                caminho, 
                                encoding=encoding,
                                sep=separador,
                                engine='python',
                                on_bad_lines='skip'
                            )
                        
                        if df is not None:
                            break
                            
                    except Exception as e:
                        print(f"Erro com encoding {encoding}: {str(e)}")
                        continue
                
                if df is not None:
                    return df.fillna("").astype(str)
                else:
                    return "Erro: Não foi possível ler o arquivo com nenhum encoding"
                
            else:
                return f"Arquivo {file['name']} não suportado"
                    
        except Exception as e: 
            return f"Erro crítico: {str(e)}"
        
    @output
    @render.ui
    def escolha_coluna():
        dados = processa_dados()
        if dados is None or not isinstance(dados, pd.DataFrame):
            return ui.p("Carregue um arquivo para selecionar a coluna de texto.")
        
        colunas_texto = list(dados.columns)
        
        return ui.input_select(
            "coluna_texto",
            "Selecione a coluna de texto:",
            choices=colunas_texto
        )
   
    @reactive.Calc
    def coluna_selecionada():
        dados = processa_dados()
        coluna = input.coluna_texto()
        
        if dados is None or not isinstance(dados, pd.DataFrame):
            return None
        if coluna not in dados.columns:
            return None
        
        return dados[coluna]

    @output
    @render.table
    def tabela_dados():
        dados = processa_dados()
        coluna = input.coluna_texto()
    
        if dados is None:
            return pd.DataFrame({"Status": ["Nenhum dado disponível"]})
        
        if not isinstance(dados, pd.DataFrame):
            return pd.DataFrame({"Erro": [str(dados)]})
        
        if dados.empty:
            return pd.DataFrame({"Status": ["DataFrame vazio"]})
        
        if coluna and coluna in dados.columns:
            outras = [c for c in dados.columns if c != coluna]
            dados = dados[[coluna] + outras]

        return dados.reset_index().astype(str).replace("nan", "").replace("None", "")
        
    @output
    @render.text
    def info_dados():
        serie = coluna_selecionada()

        if serie is None:
            return "Nenhuma coluna selecionada"
        
        total = len(serie)
        vazios = serie.isna().sum()
        media_palavras = serie.str.split().str.len().mean()

        return f"Coluna selecionada: {total} registros | Registros vazios: {vazios} | Média de palavras por registro: {media_palavras:.2f}"
    
    ########################
    # STOPWORDS
    #########################

    @output 
    @render.text
    def value():
        return str(input.stopwords())

    @reactive.Calc
    def escolha_stopwords():
        escolha = input.stopwords()
        if escolha is None:
            return []
        if escolha == "sw1":
            return stopwords_edit_sw1()
        elif escolha == "sw2":
            return stopwords_edit_sw2()
        elif escolha == "sw3":
            return stopwords_edit_sw3()
        elif escolha == "sw123":
            return stopwords_edit_sw123()
        else:
            return []

    stopwords_edit_sw1 = reactive.Value(list(stopwords_ptBR))
    stopwords_edit_sw2 = reactive.Value(list(stopwords_iso))
    stopwords_edit_sw3 = reactive.Value(list(stopwords_comentarios))
    stopwords_edit_sw123 = reactive.Value(list(all_stopwords))

    @reactive.Calc
    def conjunto_editavel():
        escolha = input.stopwords()
        if escolha == "sw1":
            return stopwords_edit_sw1
        elif escolha == "sw2":
            return stopwords_edit_sw2
        elif escolha == "sw3":
            return stopwords_edit_sw3
        elif escolha == "sw123":
            return stopwords_edit_sw123
        return stopwords_edit_sw1

    @output
    @render.table
    def tabela_edicao():
        conjunto = conjunto_editavel()
        palavras = conjunto.get()
        df = pd.DataFrame({"Palavra": sorted(palavras)})
        return df

    @reactive.Effect
    @reactive.event(input.adicionar_palavra)
    def adicionar_palavra():
        nova_palavra = input.nova_palavra().strip().lower()
        if not nova_palavra:
            return
        
        conjunto = conjunto_editavel()
        palavras_atual = set(conjunto.get())
        palavras_atual.add(nova_palavra)
        conjunto.set(sorted(list(palavras_atual)))
        ui.update_text("nova_palavra", value="")

    @reactive.Effect
    @reactive.event(input.remover_selecionadas)
    def remover_palavras():
        conjunto = conjunto_editavel()
        palavra_remover = input.nova_palavra().strip().lower()
        if not palavra_remover:
            return
            
        palavras_atual = set(conjunto.get())
        if palavra_remover in palavras_atual:
            palavras_atual.remove(palavra_remover)
            conjunto.set(sorted(list(palavras_atual)))
            ui.update_text("nova_palavra", value="")

    @reactive.Effect
    @reactive.event(input.resetar_lista)
    def resetar_lista():
        conjunto = conjunto_editavel()
        escolha = input.stopwords()
        if escolha == "sw1":
            conjunto.set(list(stopwords_ptBR))
        elif escolha == "sw2":
            conjunto.set(list(stopwords_iso))
        elif escolha == "sw3":
            conjunto.set(list(stopwords_comentarios))
        elif escolha == "sw123":
            conjunto.set(list(all_stopwords))

    @reactive.Effect
    @reactive.event(input.adicionar_palavra, input.remover_selecionadas, input.resetar_lista)
    def atualizar_visualizacoes():
        pass

    ########################
    # PRÉ-PROCESSAMENTO
    #########################
    import pandas as pd

    def remove_pontuacao_numeros(df):
        if not isinstance(df, pd.DataFrame):
            return None

        df_limpo = df.copy()

        # Seleciona todas as colunas de texto
        colunas_texto = df_limpo.select_dtypes(include=['object', 'string']).columns

        for coluna in colunas_texto:
            # Força string
            df_limpo[coluna] = df_limpo[coluna].astype(str)
            # Quebra de linha do espaço
            df_limpo[coluna] = df_limpo[coluna].str.replace('\n', ' ', regex=False)
            # Remove caracteres especiais (mantendo letras acentuadas e espaços)
            df_limpo[coluna] = df_limpo[coluna].str.replace(r'[^A-Za-zÀ-ÿ\s]', ' ', regex=True)
            # Remove números
            df_limpo[coluna] = df_limpo[coluna].str.replace(r'\d+', '', regex=True)
            # Remove espaços duplicados
            df_limpo[coluna] = df_limpo[coluna].str.replace(r'\s+', ' ', regex=True).str.strip()
        return df_limpo

    @output
    @render.table
    def tabela_sem_pontuacao_num():
        dados = processa_dados()
        if isinstance(dados, pd.DataFrame):
            return remove_pontuacao_numeros(dados)
        else:
            return None
        
    @reactive.Calc
    def remove_repeticao():
        dados = processa_dados()  
        if dados is None:
            return None
        
        if isinstance(dados, pd.DataFrame):
            dados = remove_pontuacao_numeros(dados)  

            dados_limpo = dados.copy()

            for coluna in dados_limpo.columns:
                if dados_limpo[coluna].dtype == 'object':
                    '''Remove caracteres repetidos'''
                    dados_limpo[coluna] = dados_limpo[coluna].apply(
                        lambda x: re.sub(r"([^RSrs])\1+|R{3,}|S{3,}|r{3,}|s{3,}", 
                            lambda m: m.group(0)[0:2] if m.group(0)[0] in "RrSs" else m.group(0)[0], 
                            str(x)
                        )
                    )

            return dados_limpo

        return None

    @output
    @render.table
    def tabela_sem_repeticao():
        dados = remove_repeticao()  
        if isinstance(dados, pd.DataFrame):
            return dados
        else:
            return None
        
    def lemmatizar_lista(textos):
        docs = list(nlp.pipe(textos.astype(str)))
        lemas_processados = []

        for doc in docs:
            palavras_lematizadas = [token.lemma_.lower() for token in doc]
            lemas_processados.append(" ".join(palavras_lematizadas))

        return lemas_processados

    @reactive.Calc
    def texto_lemmatizado():
        dados = remove_repeticao()
        if dados is None or dados.empty:
            return None

        col = input.coluna_texto()
        if not col or col not in dados.columns:
            return dados

        dados = dados.copy()
        textos = dados[col].astype(str)
        stemmer = SnowballStemmer('portuguese')

        # ==========================================
        # lema por contexto (frase inteira)
        # ==========================================
        docs_contexto = list(nlp.pipe(textos.str.lower()))

        lema_por_contexto = {}  

        for doc in docs_contexto:
            for token in doc:
                palavra = token.text.lower()
                lemma = token.lemma_.lower()
                if lemma not in palavra:
                    lemma = palavra
                # só registra se ainda não viu essa palavra
                # (primeira ocorrência = contexto mais representativo)
                if palavra not in lema_por_contexto:
                    lema_por_contexto[palavra] = lemma

        # ==========================================
        # lema por palavra isolada
        # mais estável, sem erro de contexto (evitando lemmas malucos tipo lir para lindo ou areiar para areia)
        # ==========================================
        dados_freq = (
            textos
            .str.lower()
            .str.split()
            .explode()
            .dropna()
            .value_counts()
            .reset_index()
        )
        dados_freq.columns = ['Palavra', 'Frequência']
        dados_freq = dados_freq.sort_values(by='Frequência', ascending=False).reset_index(drop=True)

        docs_isolado = list(nlp.pipe(dados_freq['Palavra']))

        lema_por_isolado = {}  

        for doc, palavra in zip(docs_isolado, dados_freq['Palavra']):
            if len(doc) == 0:
                lema_por_isolado[palavra] = palavra
                continue
            lemma = doc[0].lemma_.lower()
            if lemma not in palavra:
                lemma = palavra
            lema_por_isolado[palavra] = lemma

        # ==========================================
        # stem como agrupador morfológico
        # resolve gênero/número que spaCy não agrupa
        # ==========================================
        mapa_stem = {}   # stem → representante (palavra mais frequente)
        mapa_final = {}  # palavra → representante final

        for _, row in dados_freq.iterrows():
            palavra = row['Palavra']

            lema_ctx = lema_por_contexto.get(palavra, palavra)
            lema_iso = lema_por_isolado.get(palavra, palavra)

            # decisão: prefere lema contextual, usa isolado como fallback
            # se os dois concordam → confiança alta
            # se divergem → usa o isolado (mais estável)
            if lema_ctx == lema_iso:
                lemma_escolhido = lema_ctx   # ← alta confiança
            else:
                lemma_escolhido = lema_iso   # ← fallback mais estável

            # encadeamento: se o lema escolhido já tem representante, usa ele
            if lemma_escolhido in mapa_final:
                lemma_escolhido = mapa_final[lemma_escolhido]

            # stem como ponte para variações de gênero/número
            stem = stemmer.stem(palavra)

            if stem in mapa_stem:
                representante = mapa_stem[stem]
            else:
                representante = lemma_escolhido
                mapa_stem[stem] = representante

            mapa_final[palavra] = representante

        def aplicar_lema(texto):
            tokens = str(texto).lower().split()
            return " ".join(mapa_final.get(t, t) for t in tokens)

        dados[col] = textos.apply(aplicar_lema)

        return dados

    @reactive.Calc
    def remove_acentuacao_2caracteres():
        dados_processados = texto_lemmatizado()

        if dados_processados is None or not isinstance(dados_processados, pd.DataFrame):
            print("Df vazio ou inválido")
            return None

        col = input.coluna_texto()

        if not col or col not in dados_processados.columns:
            print("Coluna inválida:", col)
            return None

        lista_excecao = [
            'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 
            'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 
            'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to', 'br', 'ir', 'km', 'ar'
        ]

        # unicode para remover acentos
        def remover_acentos(texto):
            if pd.isna(texto):
                return ""
            return ''.join(
                c for c in unicodedata.normalize('NFKD', str(texto))
                if not unicodedata.combining(c)
            )

        def remover_palavras_curta(texto):
            palavras = texto.split()
            filtradas = [
                p for p in palavras
                if len(p) > 2 or p.lower() in lista_excecao
            ]
            return ' '.join(filtradas)

        serie = dados_processados[col].astype(str)

        coluna_tratada = (
            serie
            .apply(remover_acentos)
            .str.lower()
            .apply(remover_palavras_curta)
            .str.replace(r'\s+', ' ', regex=True)
            .str.strip()
        )

        return pd.DataFrame({
            "Sem acento e sem palavras curtas": coluna_tratada
        })

    @output
    @render.table
    def tabela_acentuacao_2caracteres():
        dados = remove_acentuacao_2caracteres()
        return dados


    @reactive.Calc
    def remove_stopw_minuscula():
        tabela_editada = conjunto_editavel().get() or []

        # Normaliza stopwords: remove acento + lemmatiza
        def normalizar_stopword(s):
            return ''.join(
                c for c in unicodedata.normalize('NFKD', s)
                if not unicodedata.combining(c)
            ).lower().strip()

        tabela_editada = [normalizar_stopword(s) for s in tabela_editada]

        # ✅ Use remove_acentuacao_2caracteres() — já normalizado
        dados = remove_acentuacao_2caracteres()

        if dados is None or not isinstance(dados, pd.DataFrame):
            return None

        dados_stopw = dados.copy()
        coluna = "Sem acento e sem palavras curtas"  # nome da coluna gerada por remove_acentuacao_2caracteres

        if coluna not in dados_stopw.columns:
            return dados_stopw

        def remover_stopwords_tokens(texto):
            if pd.isna(texto):
                return texto
            palavras = str(texto).lower().split()
            return " ".join(p for p in palavras if p not in tabela_editada)

        dados_stopw[coluna] = dados_stopw[coluna].apply(remover_stopwords_tokens)

        return dados_stopw

    @output
    @render.table
    def tabela_sem_stopwords_minuscula():
        dados = remove_stopw_minuscula()  
        if isinstance(dados, pd.DataFrame):
            return dados
        else:
            return None
        
    def calcular_frequencia(df, n=1):
        if df is None or df.empty:
            return pd.DataFrame(columns=["Ngrama", "Frequência"])

        coluna = df.columns[0]

        if coluna not in df.columns:
            return pd.DataFrame(columns=["Ngrama", "Frequência"])

        series_ngrams = (
            df[coluna]
            .dropna()
            .astype(str)
            .str.lower()
            .str.split()
        )

        ngramas = []

        for tokens in series_ngrams:
            if len(tokens) < n:
                continue

            for i in range(len(tokens) - n + 1):
                ngrama = " ".join(tokens[i:i+n])
                ngramas.append(ngrama)

        df_ngrams = (
            pd.Series(ngramas)
            .value_counts()
            .reset_index()
        )

        df_ngrams.columns = ["Ngrama", "Frequência"]

        return df_ngrams
    
    ########################
    # TABELA DE FREQUÊNCIA
    #########################

    @reactive.Calc
    def tabela_ngram():
        escolha = input.frequencia_tipo()

        if escolha == "palavras":
            n = 1
        elif escolha == "bigramas":
            n = 2
        elif escolha == "trigramas":
            n = 3
        elif escolha == "tetragramas":
            n = 4
        elif escolha == "pentagramas":
            n = 5
        else:
            return None

        return calcular_frequencia(remove_stopw_minuscula(), n=n)

    @output
    @render.table
    def tabela_frequencia():
        return tabela_ngram()

    ########################
    # GRÁFICO DE FREQUÊNCIA
    #########################

    def grafico_ngrama(df, n=1, top_n=20):
        freq = calcular_frequencia(df, n=n)

        if freq is None or freq.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Nenhum dado para exibir", ha='center', va='center', fontsize=16)
            ax.axis('off')
            return fig

        top_freq = freq.head(top_n)

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='Frequência', y=freq.columns[0], data=top_freq, palette='viridis', ax=ax)
        ax.set_title(f'{n}-gramas mais frequentes')
        ax.set_xlabel('Frequência')
        ax.set_ylabel('Ngrama')
        fig.tight_layout()
        return fig

    @output
    @render.plot
    def grafico_ngram():
        n = input.ngram_n()  # pega valor do slider
        df_processado = remove_stopw_minuscula()
        return grafico_ngrama(df_processado, n=n)

    ########################
    # NUVENS DE PALAVRAS
    #########################

    def nuvem_ngrama(df, n=1, coluna_texto="coments", max_words=50):

        freq = calcular_frequencia(df, n=n)

        if freq is None or freq.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Nenhum dado para exibir", ha='center', va='center', fontsize=16)
            ax.axis('off')
            return fig

        freq_dict = dict(zip(freq[freq.columns[0]], freq['Frequência']))

        # Cria nuvem
        nuvem = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=max_words
        ).generate_from_frequencies(freq_dict)

        # Plota
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(nuvem, interpolation="bilinear")
        ax.axis('off')
        return fig

    @output
    @render.plot
    def nuvem_ngram():
        n = input.ngram_n()  # pega valor do slider
        max_words = input.max_words() if input.max_words() is not None else 50
        df_processado = remove_stopw_minuscula()  
        return nuvem_ngrama(df_processado, n=n, coluna_texto="coments", max_words=max_words)

    ########################
    # ANÁLISE DE TÓPICOS - MODELO LDA: Latent Dirichlet Allocation
    #########################

    def analise_topicos(df, k):
        df = calcular_frequencia(df, n=1)
        
        df["id"] = range(len(df))

        # transforma df em matriz
        dtm = df.pivot_table(
            index="id",
            columns="Ngrama",
            values="Frequência",
            fill_value=0
        )

        lda = LatentDirichletAllocation(n_components=k, random_state=42)
        
        # treinamento do modelo
        lda.fit(dtm)

        topicos = []

        # lda.components_ atribui peso as palavras no tópicos
        # topico_idx = indice do tópico, termo_idx = indice do termo, value/beta = peso do termo no tópico
        for topico_idx, topico in enumerate(lda.components_):
            for termo_idx, value in enumerate(topico):
                topicos.append({
                    "Tópico": topico_idx,
                    "Termo": dtm.columns[termo_idx],
                    "Peso": value
                })
        
        topicos_df = pd.DataFrame(topicos)

        # normaliza os pesos numa escala de 0 a 1 dentro de cada tópico
        topicos_df["Peso"] = topicos_df.groupby("Tópico")["Peso"].transform(
            lambda x: x / x.sum()
        )

        return topicos_df.sort_values(by=["Tópico", "Peso"], ascending=[True, False])

    @reactive.Calc
    def tabela_topicos():
        df_processado = remove_stopw_minuscula()
        k = input.num_topicos() if input.num_topicos() is not None else 5
        return analise_topicos(df_processado, k=k)
        
    @output
    @render.table
    def tabela_analise_topicos():
        return tabela_topicos()

    @output
    @render.plot
    def grafico_analise_topicos():
        k = input.num_topicos() if input.num_topicos() is not None else 5
        df_processado = remove_stopw_minuscula()
        
        df_topicos = tabela_topicos()

        n_termos = input.termos() if input.termos() is not None else 10

        # pegar segundo n_termos por tópico
        df_topicos = (
            df_topicos
            .groupby("Tópico")
            .head(n_termos)
        )

        # fazendo 1 gráfico só para todos os tópicos
        fig, ax = plt.subplots()
        
        for topico in df_topicos["Tópico"].unique():
            subset = df_topicos[df_topicos["Tópico"] == topico]
            ax.bar(subset["Termo"], subset["Peso"], label=f"Tópico {topico}")
        
        ax.legend()
        plt.xticks(rotation=90)
        
        return fig

    ########################
    # CLUSTERIZAÇÃO
    #########################
    #utilizar baseado por frequencia absoluta
    #olhar código daphne

    ########################
    # KMEANS
    #########################
