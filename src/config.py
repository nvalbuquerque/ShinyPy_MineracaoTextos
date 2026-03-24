import os

CSS_STYLES = """
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

    .shiny-table-container {
        max-height: 500px !important;
        overflow-y: auto !important;
        border: 1px solid #ddd !important;
        border-radius: 5px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    .shiny-table thead th {
        position: sticky !important;
        top: 0 !important;
        z-index: 10 !important;
    }
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "stopwords")


def load_file(filename):
    """Carrega um arquivo .txt do diretório data e retorna lista de linhas."""
    path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    except Exception as e:
        print(f"Erro ao ler {filename}: {e}")
        return []


def load_stopwords():
    """Carrega todas as listas de stopwords dos arquivos locais .txt."""
    stopwords_ptBR = load_file("stopwords_ptBR.txt")
    stopwords_comentarios = load_file("stopwords_comentarios.txt")
    stopwords_iso = load_file("stopwords_iso.txt")
    all_stopwords = load_file("all_stopwords.txt")

    return {
        "stopwords_ptBR": stopwords_ptBR,
        "stopwords_comentarios": stopwords_comentarios,
        "stopwords_iso": stopwords_iso,
        "all_stopwords": all_stopwords,
    }

