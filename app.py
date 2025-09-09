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
                ui.input_radio_buttons(
                    "stopwords",
                    "Selecione uma lista de stopwords:",
                    choices={
                        "sw1": "Stopword 1 (pt_BR)",
                        "sw2": "Stopword 2 (pt_ISO)",
                        "sw3": "Stopword 3 (portuguese)",
                        "sw123": "Stopword 1, 2 e 3",
                    },
                    selected="sw1"
                ),
                ui.input_selectize(
                    "remove_stopwords",
                    "Remover stopwords:",
                    choices=[""] + [teste for teste in range(0, 11)],
                    selected=None,
                    multiple=False,
                    options={"allowEmptyOption": True,
                             "placeholder": "Busque as stopwords"}, 
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
                ui.nav_menu("Palavras removidas",
                    ui.nav_panel("Stopword 1",
                        ui.output_text("stopwords_selecionadas"),
                    ), 
                    ui.nav_panel("Stopword 2",
                        "Teste stopword 2",
                    ), 
                    ui.nav_panel("Stopword 3",
                        "Teste stopword 3",
                    ), 
                    ui.nav_panel("Stopword 1, 2 e 3",
                        "Teste stopword 1, 2 e 3",
                    ), 
                ),  
                ui.nav_panel("Editar stopwords"),  
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
            if file['name'].endswith('.csv'):
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        with open(caminho, 'r', encoding=encoding) as f:
                            primeira_linha = f.readline()
                        
                        if primeira_linha.count(';') > primeira_linha.count(','):
                            separador = ';'
                        else:
                            separador = ','
                        
                        df = pd.read_csv(
                            caminho, 
                            encoding=encoding,
                            sep=separador,
                            engine='python',
                            on_bad_lines='skip'
                        )
                        break
                    except:
                        continue
                else:
                    return "Erro: Não foi possível ler o arquivo CSV"
                
                return df.fillna("").astype(str)
                        
            elif file['name'].endswith('.txt'):
                with open(caminho, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Arquivo {file['name']} não suportado"
                    
        except Exception as e: 
            return f"Erro: {str(e)}"

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
        
        elif isinstance(dados, str):
            if not dados or dados.strip() == "":
                return pd.DataFrame({"Status": ["Texto vazio"]})
            df = pd.DataFrame({
                "Índice": range(len(dados.splitlines())),
                "Conteúdo": dados.splitlines()
            })
            return df.astype(str).replace("nan", "").replace("None", "")
        
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
        
        elif isinstance(dados, str) and "Erro:" in dados:
            return dados
        
        elif isinstance(dados, str):
            return f"Informações: {len(dados)} caracteres"
        
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
            return stopwords_ptBR
        elif escolha == "sw2":
            return stopwords_iso
        elif escolha == "sw3":
            return stopwords_comentarios
        elif escolha == "sw123":
            return sorted(list(all_stopwords))
        else:
            return []

    @output
    @render.text
    def stopwords_selecionadas():
        try:
            sw = escolha_stopwords()
            if not sw: 
                return "Nenhuma lista de stopwords selecionada."
            return f"Stopwords selecionadas: {len(sw)}. Primeiras 20: {', '.join(sw[:20])}"
        
        except Exception as e:
            return f"Erro ao carregar stopwords: {str(e)}"

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=0)
