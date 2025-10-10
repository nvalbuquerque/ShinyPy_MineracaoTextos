import nltk
import requests
from nltk.corpus import stopwords

NLTK_PACKAGES = ['stopwords', 'punkt']

STOPWORDS_URL = "https://jodavid.github.io/Slide-Introdu-o-a-Web-Scrapping-com-rvest/stopwords_pt_BR.txt"

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
"""

def download_nltk_data():
    """Download do NLTK - código original"""
    for package in NLTK_PACKAGES:
        try:
            nltk.data.find(package)
        except LookupError:
            print(f"Downloading NLTK package: {package}")
            nltk.download(package, quiet=True)

def load_stopwords():
    """Carrega stopwords - código original"""
    download_nltk_data()
    
    response = requests.get(STOPWORDS_URL)
    stopwords_ptBR = response.text.splitlines()
    stopwords_comentarios = stopwords.words('portuguese')
    stopwords_iso = sorted(stopwords.words('portuguese'))  

    all_stopwords = set(stopwords_comentarios + stopwords_ptBR + list(stopwords_iso))
    all_stopwords.difference_update(["não", "nao"])

    return {
        'stopwords_ptBR': stopwords_ptBR,
        'stopwords_comentarios': stopwords_comentarios, 
        'stopwords_iso': stopwords_iso,
        'all_stopwords': all_stopwords
    }