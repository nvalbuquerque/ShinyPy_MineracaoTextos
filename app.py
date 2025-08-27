from shiny import App, ui, reactive, render
import pandas as pd

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
                bg="#f8f8f8",
                open="open",
            ),
            ui.page_navbar(  
            ui.nav_panel("Dados importados", ui.output_text("info_dados"), ui.output_table("tabela_dados")),  
            ui.nav_panel("Palavras removidas"),  
            ui.nav_panel("Editar stopwords"),  
            ui.nav_panel("Pré-processamento"),  
            ui.nav_panel("Tabela de Frequência"),  
            ui.nav_panel("Gráfico de Frequência"),
            ui.nav_panel("Nuvens de palavras"),  
            ui.nav_panel("Análise de tópicos"),  
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
                try:
                    return pd.read_csv(caminho, encoding='utf-8')
                except:
                    return pd.read_csv(caminho, on_bad_lines='skip', encoding='utf-8')
            elif file['name'].endswith('.txt'):
                with open(caminho, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Arquivo {file['name']} não suportado"
            
        except Exception as e: return f"Erro: {str(e)}"
        
    @output()
    @render.table()
    def tabela_dados():
        dados = processa_dados()
        if dados is None:
            return None
        elif isinstance(dados, str):
            return pd.DataFrame({'Conteúdo': [dados]})
        elif isinstance(dados, pd.DataFrame):
            return dados
        return None
    
    @output()
    @render.text()
    def info_dados():
        dados = processa_dados()
        if dados is None:
            return None
        elif isinstance(dados, str):
            if "Erro:" in dados:
                return dados 
            return f"Informações: {len(dados)} caracteres"
        elif isinstance(dados, pd.DataFrame):
            return f"Informações: {len(dados)} linhas e {len(dados.columns)} colunas"
        else:
            return f"Dados carregados: {type(dados).__name__}"

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=8080)
