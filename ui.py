from shiny import ui
from config import CSS_STYLES

def create_ui():
    return ui.page_fillable(
        ui.tags.head(
            ui.tags.style(CSS_STYLES),
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
                    ui.input_slider("altura", "Altura", min=100, max=800, value=550),
                    ui.input_slider("largura", "Largura", min=100, max=800, value=650),
                    bg="#f8f8f8",
                    open="open",
                ),

                ui.page_navbar(
                    ui.nav_panel(
                        "Dados importados",
                        ui.output_text("info_dados"),
                        ui.output_table("tabela_dados"),
                    ),

                    ui.nav_panel(
                        "Editar lista de stopwords",
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

                        ui.layout_columns(
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
                        ui.output_text("status_edicao"),
                    ),

                    ui.nav_menu(
                        "Pré-processamento",
                        ui.nav_panel(
                            "Remove pontuação e números",
                            ui.output_table("tabela_sem_pontuacao_num"),
                        ),
                        ui.nav_panel(
                            "Remove caracteres repetidos",
                            ui.output_table("tabela_sem_repeticao"),
                        ),
                        ui.nav_panel(
                            "Remove stopwords e converte para minúsculo",
                            ui.output_table("tabela_sem_stopwords_minuscula"),
                        ),
                        ui.nav_panel(
                            "Remove acentuação e dois caracteres",
                            ui.output_table("tabela_acentuacao_2caracteres"),
                        ),
                        ui.nav_panel(
                            "Elege representante",
                            ui.output_table("tabela_elege_representante"),
                        ),
                        
                    ),

                    ui.nav_panel(
                        "Tabela de Frequência",
                        ui.input_radio_buttons(
                        "frequencia_tipo",
                        "Selecione o tipo de n-grama:",
                            choices={
                                "palavras": "Palavras",
                                "bigramas": "Bigramas",
                                "trigramas": "Trigramas",
                                "tetragramas": "Tetragramas",
                                "pentagramas": "Pentagramas",
                            },
                            selected="palavras",
                            inline=True
                        ),
                        ui.output_table("tabela_frequencia")
                    ),

                    ui.nav_panel("Gráfico de Frequência",
                        # Slider para escolher n
                        ui.input_slider(
                            "ngram_n", "Escolha n-grama:", min=1, max=5, value=1, step=1
                        ),
                        # Local para o gráfico
                        ui.output_plot("grafico_ngram")  
                    ),

                    ui.nav_panel(
                        "Nuvem de palavras",
                        # Slider para escolher o número máximo de palavras na nuvem
                        ui.layout_columns (
                            ui.input_slider(
                            "ngram_n", "Escolha n-grama:", min=1, max=5, value=1, step=1
                        ),
                        ui.input_slider(
                            "max_words",
                            "Número máximo de palavras na nuvem:",
                            min=10,
                            max=100,
                            value=50,
                            step=10
                        ),
                        col_widths=(6, 6)
                        ),
                        ui.output_plot("nuvem_ngram")
                    ),

                    ui.nav_panel(
                        "Análise de tópicos",
                        ui.layout_columns(
                            ui.input_slider(
                            "termos", "Número de termos a serem representados:", min=1, max=50, value=10, step=1
                            ),
                            ui.input_slider(
                                "num_topicos", "Número de tópicos:", min=2, max=10, value=5, step=1
                            ),
                            col_widths=(6, 6)
                        ),
                        ui.output_plot("grafico_analise_topicos"),
                        ui.output_table("tabela_analise_topicos")
                    ),

                    ui.nav_panel("Sentimentos"),
                    ui.nav_panel("Clusterização"),
                    ui.nav_panel("KMeans"),
                    ui.nav_panel("Redes"),

                    id="page",
                ),
            ),
        ),
    )
