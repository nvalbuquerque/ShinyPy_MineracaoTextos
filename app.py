from shiny import App, ui, reactive, render
import pandas as pd
import requests
import nltk
from nltk.corpus import stopwords

nltk_packages = ['stopwords', 'punkt']

def download_nltk_data():
    for package in nltk_packages:
        try:
            nltk.data.find(package)
        except LookupError:
            print(f"Downloading NLTK package: {package}")
            nltk.download(package, quiet=True)

download_nltk_data()

url = "https://jodavid.github.io/Slide-Introdu-o-a-Web-Scrapping-com-rvest/stopwords_pt_BR.txt"
response = requests.get(url)
stopwords_ptBR = response.text.splitlines()
stopwords_comentarios = stopwords.words('portuguese')
stopwords_iso = sorted(stopwords.words('portuguese'))  

all_stopwords = set(stopwords_comentarios + stopwords_ptBR + list(stopwords_iso))
all_stopwords.difference_update(["não", "nao"])

app_ui = ui.page_fillable(

    ui.tags.head(
        ui.tags.style("""
            
            /* Texto do input */
            .shiny-input-container input {
                font-size: 12px !important;
            }
            
            /* Botão de procurar */
            .btn-default {
                font-size: 12px !important;
                width: 100% !important;
            }
            
            /* Label do botão */
            .btn-default .btn-label {
                font-size: 12px !important;
            }
                      
            /* ESTILO PARA TABELAS SHINY */
            .shiny-table {
                width: 100% !important;
                border-collapse: collapse !important;
                font-size: 12px !important;
                margin: 10px 0 !important;
            }
            
            .shiny-table th {
                background-color: #f8f9fa !important;
                padding: 10px !important;
                text-align: left !important;
                border: 1px solid #dee2e6 !important;
                font-weight: bold !important;
                color: #495057 !important;
            }
            
            .shiny-table td {
                padding: 8px !important;
                border: 1px solid #dee2e6 !important;
                text-align: left !important;
            }
            
            .shiny-table tr:nth-child(even) {
                background-color: #f8f9fa !important;
            }
            
            .shiny-table tr:hover {
                background-color: #e9ecef !important;
                transition: background-color 0.2s ease;
            }
            
            /* Container da tabela */
            .shiny-table-container {
                max-height: 500px !important;
                overflow-y: auto !important;
                border: 1px solid #ddd !important;
                border-radius: 5px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            }
            
            /* Header fixo para scroll */
            .shiny-table thead th {
                position: sticky !important;
                top: 0 !important;
                z-index: 10 !important;
            }
        """),
    ),

    ui.card(
        ui.card_header("Mineração de Textos"),

        ui.layout_sidebar(
            ui.sidebar(
                ui.input_file(
                    "file1", 
                    label="Selecione um arquivo",
                    multiple=False, 
                    accept=".txt, .csv",
                    placeholder="Nenhum arquivo selecionado",
                    button_label="Procurar",
                ),
                ui.input_slider("altura", "Altura", min = 100, max = 800 , value = 550),
                ui.input_slider("largura", "Largura", min = 100, max = 800 , value = 650),
                bg="#f8f8f8",
                open="open",
            ),

            ui.page_navbar(  
                ui.nav_panel("Dados importados",
                    ui.output_text("info_dados"),
                    ui.output_table("tabela_dados")
                ),
                ui.nav_menu("Visualização das listas de stopwords",
                    ui.nav_panel("Stopword 1",
                        ui.output_table("tabela_stopwords_1"),
                    ), 
                    ui.nav_panel("Stopword 2",
                        ui.output_table("tabela_stopwords_2"),
                    ), 
                    ui.nav_panel("Stopword 3",
                        ui.output_table("tabela_stopwords_3"),
                    ), 
                    ui.nav_panel("Stopword 1, 2 e 3",
                        ui.output_table("tabela_stopwords_123"),
                    ), 
                ), 
                ui.nav_panel("Editar lista de stopwords selecionada",
                    ui.input_radio_buttons(
                        "stopwords",
                        "Selecione uma lista de stopwords:",
                        choices={
                            "sw1": "Stopword 1 (pt_BR)",
                            "sw2": "Stopword 2 (pt_ISO)",
                            "sw3": "Stopword 3 (portuguese)",
                            "sw123": "Stopword 1, 2 e 3",
                        },
                        selected="sw1",
                        inline=True
                    ),
                     ui.layout_columns(  # ← BOTÕES EM LINHA
                         ui.input_text(
                            "nova_palavra",
                            None,
                            placeholder="Digite uma palavra...", 
                        ),
                        ui.input_action_button(
                            "adicionar_palavra",
                            "Adicionar palavra",
                        ),
                        ui.input_action_button(
                            "remover_selecionadas", 
                            "Remover palavra",
                        ),
                        ui.input_action_button(
                            "resetar_lista",
                            "Resetar para original",
                        ),
                        col_widths=(3, 3, 3, 3)  
                    ),
                    ui.output_table("tabela_edicao"),
                    ui.output_text("status_edicao")
                ),  
                ui.nav_menu("Pré-processamento",
                    ui.nav_panel("Remove pontuação e números",
                        "Teste Remove pontuação e números",
                    ), 
                    ui.nav_panel("Remove caracteres repetidos",
                        "Teste Remove caracteres repetidos",
                    ), 
                    ui.nav_panel("Remove stopwords e converte para minúsculo",
                        "Teste Remove stopwords e converte para minúsculo",
                    ), 
                    ui.nav_panel("Retira plural",
                        "Teste Retira plural",
                    ),
                    ui.nav_panel("Elege representante",
                        "Teste Elege representante",
                    ),
                    ui.nav_panel("Remove acentuação e dois caracteres",
                        "Teste Remove acentuação e dois caracteres",
                    ), 
                ),  
                ui.nav_menu("Tabela de Frequência",
                    ui.nav_panel("Palavras",
                        "Teste Palavras",
                    ),
                    ui.nav_panel("Bigramas",
                        "Teste Bigramas",
                    ),
                    ui.nav_panel("Trigramas",
                        "Teste Trigramas",
                    ),
                    ui.nav_panel("Tetragramas",
                        "Teste Tetragramas",
                    ),
                    ui.nav_panel("Pentagramas",
                        "Teste Pentagramas",
                    ),
                ),
                ui.nav_menu("Gráfico de Frequência",
                    ui.nav_panel("Palavras",
                        "Teste Palavras",
                    ),
                    ui.nav_panel("Bigramas",
                        "Teste Bigramas",
                    ),
                    ui.nav_panel("Trigramas",
                        "Teste Trigramas",
                    ),
                    ui.nav_panel("Tetragramas",
                        "Teste Tetragramas",
                    ),
                    ui.nav_panel("Pentagramas",
                        "Teste Pentagramas",
                    ),
                ),
                ui.nav_menu("Nuvens de palavras",
                    ui.nav_panel("Palavras",
                        "Teste Palavras",
                    ),
                    ui.nav_panel("Bigramas",
                        "Teste Bigramas",
                    ),
                    ui.nav_panel("Trigramas",
                        "Teste Trigramas",
                    ),
                    ui.nav_panel("Tetragramas",
                        "Teste Tetragramas",
                    ),
                    ui.nav_panel("Pentagramas",
                        "Teste Pentagramas",
                    ),
                ),  
                ui.nav_menu("Análise de tópicos",
                    ui.nav_panel("Palavras",
                        "Teste Palavras",
                    ),
                    ui.nav_panel("Bigramas",
                        "Teste Bigramas",
                    ),
                    ui.nav_panel("Trigramas",
                        "Teste Trigramas",
                    ),
                    ui.nav_panel("Tetragramas",
                        "Teste Tetragramas",
                    ),
                    ui.nav_panel("Pentagramas",
                        "Teste Pentagramas",
                    ),
                ),  
                ui.nav_panel("Sentimentos"),
                ui.nav_panel("Clusterização"),  
                ui.nav_panel("KMeans"),  
                ui.nav_panel("Redes"),
                id="page",  
            ),
        ),
    )
)

def server(input, output, session):
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
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
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

    @output
    @render.table
    def tabela_stopwords_1():
        return pd.DataFrame({"Stopwords": list(stopwords_ptBR)})

    @output
    @render.table
    def tabela_stopwords_2():
        return pd.DataFrame({"Stopwords": list(stopwords_iso)})

    @output
    @render.table
    def tabela_stopwords_3():
        return pd.DataFrame({"Stopwords": list(stopwords_comentarios)})

    @output
    @render.table
    def tabela_stopwords_123():
        return pd.DataFrame({"Stopwords": sorted(list(all_stopwords))})


    stopwords_edit_sw1 = reactive.Value(list(stopwords_ptBR))
    stopwords_edit_sw2 = reactive.Value(list(stopwords_iso))
    stopwords_edit_sw3 = reactive.Value(list(stopwords_comentarios))
    stopwords_edit_sw123 = reactive.Value(list(all_stopwords))

    @output
    @render.table
    def tabela_stopwords_1():
        return pd.DataFrame({"Stopwords": stopwords_edit_sw1.get()})

    @output
    @render.table
    def tabela_stopwords_2():
        return pd.DataFrame({"Stopwords": stopwords_edit_sw2.get()})

    @output
    @render.table
    def tabela_stopwords_3():
        return pd.DataFrame({"Stopwords": stopwords_edit_sw3.get()})

    @output
    @render.table
    def tabela_stopwords_123():
        return pd.DataFrame({"Stopwords": sorted(stopwords_edit_sw123.get())})

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

        df = pd.DataFrame({
            "Palavra": sorted(palavras),
        })
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

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=0)