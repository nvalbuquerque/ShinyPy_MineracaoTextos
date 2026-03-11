from shiny import reactive, render, ui
import pandas as pd
import string
import re
import io
from datetime import datetime
import nltk
from nltk.stem.snowball import SnowballStemmer
from config import load_stopwords
import spacy
# Biblioteca média de língua portuguesa no spaCy
nlp = spacy.load("pt_core_news_md")
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

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
    @render.table
    def tabela_dados():
        dados = processa_dados()
    
        if dados is None:
            return pd.DataFrame({"Status": ["Nenhum dado disponível"]})
        
        elif isinstance(dados, pd.DataFrame):
            if dados.empty:
                return pd.DataFrame({"Status": ["DataFrame vazio"]})
            return dados.reset_index().astype(str).replace("nan", "").replace("None", "")
        
        else:
            try:
                df = pd.DataFrame(dados)
                return df.reset_index().astype(str).replace("nan", "").replace("None", "")
            except:
                return pd.DataFrame({"Erro": ["Não foi possível processar os dados"]})
        
    @output
    @render.text
    def info_dados():
        dados = processa_dados()
        
        if dados is None:
            return "Nenhum dado carregado"
        
        elif isinstance(dados, pd.DataFrame):
            missing = dados.isna().sum()
            total_missing = missing.sum()
                
            return (
                f"Informações: {len(dados)} linhas e {len(dados.columns)} colunas | "
                f"Quantidade de valores faltantes: {total_missing}"            
            )
        
        else:
            return "Tipo de dado não reconhecido"
    
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

    # Teste rápido
    teste = pd.DataFrame({"texto": ["Olá! Tudo bem? 123", "Teste, nova-linha.\n"]})
    df2 = remove_pontuacao_numeros(teste)
    print(df2)

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
        

    @reactive.Calc
    def remove_stopw_minuscula():
        tabela_editada = conjunto_editavel().get() or []

        if tabela_editada is None:
            tabela_editada = []
        
        tabela_editada = [str(s).strip().lower() for s in tabela_editada if str(s).strip() != ""]

        print("Stopwords recebidas:", tabela_editada)

        dados = remove_repeticao()

        if dados is None or not isinstance(dados, pd.DataFrame):
            print("remove_repeticao retornou vazio")
            return None

        dados_stopw = dados.copy()

        # Não montar regex se stopwords estiverem vazias
        if len(tabela_editada) == 0:
            return dados_stopw

        # Seleciona todas as colunas de texto (object ou string)
        colunas_texto = dados_stopw.select_dtypes(include=['object', 'string']).columns

        for coluna in dados_stopw.columns:
            def remover_stopwords_tokens(texto):
                if pd.isna(texto):
                    return texto
                palavras = str(texto).lower().split()
                palavras_filtradas = [p for p in palavras if p not in tabela_editada]
                return " ".join(palavras_filtradas)
            dados_stopw[coluna] = dados_stopw[coluna].apply(remover_stopwords_tokens)

        print("Dados após remover stopwords:")
        print(dados_stopw.head())

        return dados_stopw


    @output
    @render.table
    def tabela_sem_stopwords_minuscula():
        dados = remove_stopw_minuscula()  
        if isinstance(dados, pd.DataFrame):
            return dados
        else:
            return None
        
    def lemmatizar_texto(texto):
        if pd.isna(texto):
            return texto
        doc = nlp(str(texto))
        return " ".join([token.lemma_ for token in doc])

    @reactive.Calc
    def texto_lemmatizado():
        dados = remove_stopw_minuscula()

        if dados is None or dados.empty:
            return None

        col = "coments"  # ou sua coluna textual

        dados[col] = dados[col].apply(lemmatizar_texto)

        return dados
        
    @reactive.Calc 
    def remove_acentuacao_2caracteres():
        dados_processados = texto_lemmatizado()
        
        print(dados_processados.head())

        if dados_processados is None or not isinstance(dados_processados, pd.DataFrame):
            print("Df vazio")
            return None

        print("DEBUG - colunas do DF:", list(dados_processados.columns))
        
        colunas_texto = dados_processados.select_dtypes(
            include=['object', 'string']
        ).columns.tolist()

        colunas_texto = [c for c in colunas_texto if c.lower() != 'id']

        if len(colunas_texto) == 0:
            print("Nenhuma coluna textual válida encontrada")
            return None
        
        col = colunas_texto[0]
    
        lista_excecao = [
            'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 
            'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 
            'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to', 'br', 'ir', 'km', 'ar'
        ]
    
        def remover_acentos(texto):
            if pd.isna(texto):
                return texto
            mapa_acentos = str.maketrans(
                "áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ",
                "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC"
            )
            return str(texto).translate(mapa_acentos)
            
        regex_com_excecoes = r'\b(?!' + '|'.join(lista_excecao) + r')\w{1,2}\b'
            
        coluna_tratada = (
            dados_processados[col]
            .apply(remover_acentos)
            .str.replace(regex_com_excecoes, '', regex=True)
            .str.replace(r'\s+', ' ', regex=True)
            .str.strip()
        )

        return pd.DataFrame({
            "Sem acento e 2 caracteres": coluna_tratada
        })

    @output
    @render.table
    def tabela_acentuacao_2caracteres():
        dados = remove_acentuacao_2caracteres()
        return dados

    def calcular_frequencia(df, n=1):
        if df is None or df.empty:
            return pd.DataFrame(columns=["Ngrama", "Frequência"])

        coluna = df.columns[0]

        series_ngrams = (
            df[coluna]
            .dropna()
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

    @reactive.Calc
    def frequencia_absoluta():
        dados_processados = remove_acentuacao_2caracteres()
        return calcular_frequencia(dados_processados)

    @reactive.Calc
    def elege_representante():
        freq = frequencia_absoluta()

        print("DEBUG - colunas do DF:", list(freq.columns))

        if freq is None or freq.empty:
            return pd.DataFrame(columns=["Palavra_Lemmatizada"])

        return pd.DataFrame({
            "Palavra_Lemmatizada": freq["Ngrama"]
        })

    @output
    @render.table
    def tabela_elege_representante():
        dados = elege_representante()
        return dados
    
    ########################
    # TABELA DE FREQUÊNCIA
    #########################

    @output
    @render.table
    def tabela_frequencia():
        return calcular_frequencia(remove_acentuacao_2caracteres())
    
    @output
    @render.table
    def tabela_bigramas():
        return calcular_frequencia(remove_acentuacao_2caracteres(), n=2)
    
    @output
    @render.table
    def tabela_trigramas():
        return calcular_frequencia(remove_acentuacao_2caracteres(), n=3)
    
    @output
    @render.table
    def tabela_tetragramas():
        return calcular_frequencia(remove_acentuacao_2caracteres(), n=4)

    @output
    @render.table
    def tabela_pentagramas():
        return calcular_frequencia(remove_acentuacao_2caracteres(), n=5)

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
        df_processado = remove_acentuacao_2caracteres()
        return grafico_ngrama(df_processado, n=n)

    ########################
    # NUVENS DE PALAVRAS
    #########################

    #### INCLUIR QUANTIDADE DE PALAVRAS A SEREM REPRESENTADAS NA NUVEM DE PALAVRAS ####

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
        df_processado = remove_acentuacao_2caracteres()  
        return nuvem_ngrama(df_processado, n=n, coluna_texto="coments")

    ########################
    # ANÁLISE DE TÓPICOS
    #########################

    ########################
    # SENTIMENTOS
    #########################

    ########################
    # CLUSTERIZAÇÃO
    #########################

    ########################
    # KMEANS
    #########################

    ########################
    # REDES
    #########################