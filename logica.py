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
nlp = spacy.load("pt_core_news_sm")


stopwords_data = load_stopwords()
stopwords_ptBR = stopwords_data['stopwords_ptBR']
stopwords_comentarios = stopwords_data['stopwords_comentarios']
stopwords_iso = stopwords_data['stopwords_iso']
all_stopwords = stopwords_data['all_stopwords']

def lemmatizar_texto(texto):
    if pd.isna(texto):
        return texto
    doc = nlp(str(texto))
    return " ".join([token.lemma_ for token in doc])


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

    def remove_pontuacao_numeros(df):
        if isinstance(df, pd.DataFrame):
            df_limpo = df.copy()
            for coluna in df_limpo.columns:
                if df_limpo[coluna].dtype == 'object':
                    df_limpo[coluna] = df_limpo[coluna].str.replace('\n', ' ', regex=False)
                    df_limpo[coluna] = df_limpo[coluna].str.replace(r'[^\w\s]', ' ', regex=True)
                    df_limpo[coluna] = df_limpo[coluna].str.replace(r'\d+', '', regex=True)
            return df_limpo
        return None

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
        tabela_editada = conjunto_editavel().get()

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

        stopword_regex = r'\b(' + '|'.join(map(re.escape, tabela_editada)) + r')\b'

        for coluna in dados_stopw.columns:
            if dados_stopw[coluna].dtype == "object":
                if not dados_stopw[coluna].astype(str).str.contains(r"[A-Za-zÀ-ÿ]", regex=True).any():
                    continue

                dados_stopw[coluna] = (
                    dados_stopw[coluna]
                    .astype(str)
                    .str.lower()
                    .str.replace(stopword_regex, ' ', regex=True)
                    .str.replace(r'\s+', ' ', regex=True)
                    .str.strip()
                )

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

    def remover_plurais_texto(texto):
        if pd.isna(texto):
            return texto
        
        excecoes = {'variáveis': 'variável', 'tangíveis': 'tangível', 'simples': 'simples', 'mais': 'mais', 'ônibus': 'ônibus', 'cais': 'cais', 'atlas': 'atlas', 'campus': 'campus', 'bônus': 'bônus', 'status': 'status', 'lápis': 'lápis'}
        
        palavras = str(texto).split()
        resultado = []
        
        for palavra in palavras:
            if palavra in excecoes:
                resultado.append(excecoes[palavra])
            elif palavra.endswith('s'):
                if palavra.endswith(('ões', 'ãos', 'ães')): resultado.append(palavra[:-3] + 'ão')
                elif palavra.endswith('zes'): resultado.append(palavra[:-2])
                elif palavra.endswith('res'): resultado.append(palavra[:-2])
                elif palavra.endswith('ais'): resultado.append(palavra[:-2] + 'l')
                elif palavra.endswith('ns'): resultado.append(palavra[:-2] + 'm')
                elif palavra.endswith(('os', 'as', 'es')): resultado.append(palavra[:-1])
                else: resultado.append(palavra)
            else:
                resultado.append(palavra)
        
        return ' '.join(resultado)

    @reactive.Calc
    def remove_plurais():
        dados_processados = remove_stopw_minuscula()
        
        if dados_processados is None or not isinstance(dados_processados, pd.DataFrame):
            return None
        
        dados_sem_plurais = dados_processados.copy()
        
        for coluna in dados_sem_plurais.columns:
            if dados_sem_plurais[coluna].dtype == 'object':
                dados_sem_plurais[coluna] = dados_sem_plurais[coluna].apply(remover_plurais_texto)
        
        return dados_sem_plurais
    
    @output
    @render.table
    def tabela_sem_plural():
        dados = remove_plurais()
        
        if isinstance(dados, pd.DataFrame):
            return dados
        else:
            return None

    @reactive.Calc    
    def frequencia_absoluta():
        dados_processados = remove_stopw_minuscula()  # n precisa mais remove_plurais()

        if dados_processados is None or dados_processados.empty:
            print("Dados processados estão vazios.")
            return pd.DataFrame(columns=["Palavra", "Frequência"])
        
        dados_freq = dados_processados.copy()

        coluna_texto = None
        for coluna in dados_freq.columns:
            if dados_freq[coluna].dtype == 'object':
                if dados_freq[coluna].astype(str).str.contains(r"[A-Za-zÀ-ÿ]", regex=True).any():
                    coluna_texto = coluna
                    break


        if coluna_texto is None:
            print("Nenhuma coluna de texto encontrada para análise de frequência.")
            return pd.DataFrame(columns=["Palavra", "Frequência"])

        dados_freq[coluna_texto] = dados_freq[coluna_texto].apply(lemmatizar_texto)

        # Explodir e contar palavras
        dados_freq = (
            dados_freq[coluna_texto]
            .dropna()
            .str.split()
            .explode()
            .str.lower()
            .value_counts()
            .reset_index()
        )

        dados_freq.columns = ['Palavra', 'Frequência']
        dados_freq = dados_freq.sort_values(by='Frequência', ascending=False).reset_index(drop=True)
        
        return dados_freq


    @reactive.Calc
    def elege_representante():
        dados_freq = frequencia_absoluta()

        if dados_freq is None or dados_freq.empty:
            return pd.DataFrame(columns=["Palavra_Representante", "Lemma_Agrupador"])

        palavras_originais = []
        lemas_usados = []

        for _, row in dados_freq.iterrows():
            palavra = row["Palavra"]
            
            lemma = nlp(palavra)[0].lemma_.lower()
            palavra_lower = palavra.lower()

            if lemma not in lemas_usados:
                palavras_originais.append(palavra_lower)
                lemas_usados.append(lemma)

        resultado = pd.DataFrame({
            "Palavra Original": palavras_originais,
            "Palavra Lemmatizada": lemas_usados
        })

        return resultado


    @output
    @render.table
    def tabela_elege_representante():
        dados = elege_representante()
        return dados

    @reactive.Calc 
    def remove_acentuacao_2caracteres():
        dados_processados = elege_representante()
        
        if dados_processados is None or not isinstance(dados_processados, pd.DataFrame):
            return None
        
        # Garante que a coluna existe
        if "lema_usados" not in dados_processados.columns:
            return None
        
        dados_lematizados = dados_processados.copy()
    
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
        
        # --- AQUI: altera só a coluna lema_usados ---
        col = "lema_usados"
    
        dados_lematizados[col] = (
            dados_lematizados[col]
            .apply(remover_acentos)
            .str.replace(regex_com_excecoes, '', regex=True)
            .str.replace(r'\s+', ' ', regex=True)
            .str.strip()
        )
        
        return dados_lematizados[[col]]

    @output
    @render.table
    def tabela_acentuacao_2caracteres():
        dados = remove_acentuacao_2caracteres()
        return dados
