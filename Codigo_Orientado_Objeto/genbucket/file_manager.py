import os

class FileManager:
    @staticmethod
    def salvar_em_arquivo(nome_arquivo, lista):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for item in lista:
                f.write(item + "\n")

    @staticmethod
    def arquivo_existe(caminho):
        return os.path.exists(caminho)

    @staticmethod
    def verificar_dataset_valido(caminho):
        return os.path.exists(caminho) and caminho.lower().endswith(('.csv', '.txt'))
