import os
import nltk
import requests
from nltk.corpus import stopwords

STOPWORDS_URL = "https://jodavid.github.io/Slide-Introdu-o-a-Web-Scrapping-com-rvest/stopwords_pt_BR.txt"

# Diretório BASE — onde o script está rodando
BASE_DIR = os.getcwd()  # <- ALTERADO AQUI
DATA_DIR = os.path.join(BASE_DIR, "data")

print(">>> Diretório de trabalho:", BASE_DIR)
print(">>> Pasta data será criada em:", DATA_DIR)

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[OK] Pasta criada/verificada: {DATA_DIR}")

def save_list(filename, lista):
    path = os.path.join(DATA_DIR, filename)
    print(f"[SALVANDO] {path}")  # <- Print para ver se está salvando mesmo

    with open(path, "w", encoding="utf8") as f:
        for item in lista:
            f.write(item.strip() + "\n")

def gerar_stopwords():
    ensure_data_dir()

    # Baixar stopwords NLTK
    nltk.download("stopwords")
    stop_nltk = stopwords.words("portuguese")

    # Baixar via URL
    response = requests.get(STOPWORDS_URL)
    stop_ptBR = response.text.splitlines()

    # ISO (mesmo do nltk)
    stop_iso = sorted(stopwords.words("portuguese"))

    # Unificar
    all_stop = set(stop_nltk + stop_ptBR + stop_iso)
    all_stop -= {"não", "nao"}

    save_list("stopwords_ptBR.txt", stop_ptBR)
    save_list("stopwords_comentarios.txt", stop_nltk)
    save_list("stopwords_iso.txt", stop_iso)
    save_list("all_stopwords.txt", sorted(all_stop))

    print("\n✔ ARQUIVOS GERADOS COM SUCESSO ✔")


if __name__ == "__main__":
    gerar_stopwords()
