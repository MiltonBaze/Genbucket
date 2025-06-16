import os
import requests
import json

from GenBucket.GPT_neo import SeparadorFuncoes as sep


class ValidadorBucketsGPTNeo:
    def __init__(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Configuração não encontrada: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.versao = 1  # ou carregar do config futuramente
        self.pasta_base = os.path.dirname(config_path)
        self.pasta_catalogados = os.path.join(self.pasta_base, "Catalogados", f"V_{self.versao}")
        self.arquivo_filtrado = os.path.join(
            self.pasta_base,
            self.config["prompt_dir"],
            f"V_{self.versao}",
            f"Saida{self.versao}_Filtrado.txt"
        )

        os.makedirs(self.pasta_catalogados, exist_ok=True)
        sep.modoSaida = "a"
        sep.diretorioSaida = self.pasta_catalogados + "/"

        self.endpoints = [
            ".s3.amazonaws.com",
            ".storage.googleapis.com",
            ".fra1.digitaloceanspaces.com",
            ".nyc3.digitaloceanspaces.com",
            ".sgp1.digitaloceanspaces.com",
            ".ams3.digitaloceanspaces.com"
        ]

    def validar(self):
        if not os.path.exists(self.arquivo_filtrado):
            print(f"❌ Arquivo de buckets filtrados não encontrado: {self.arquivo_filtrado}")
            return

        sep.init()

        with open(self.arquivo_filtrado, "r", encoding="utf-8") as entrada:
            i = 0
            for bucket in entrada:
                bucket = bucket.strip()
                if not bucket:
                    continue
                i += 1
                try:
                    for endpoint in self.endpoints:
                        url = f"https://{bucket}{endpoint}"
                        try:
                            response = requests.head(url, timeout=10)
                            status = response.status_code
                        except requests.exceptions.RequestException as e:
                            status = None
                            sep.outros(bucket, url, f"Erro de rede: {str(e)}")
                            continue

                        if status == 200:
                            sep.publico(bucket, url)
                        elif status == 403:
                            sep.privado(bucket, url)
                        elif status == 404:
                            sep.notFound(bucket, url)
                        elif status == 400:
                            sep.outros(bucket, url, "Nome de bucket inválido")
                        else:
                            sep.outros(bucket, url, status)

                        print(f"{i} - {bucket} - {status} - {url}")

                except KeyboardInterrupt:
                    print("❌ Execução interrompida pelo usuário.")
                    break
                except Exception as e:
                    sep.outros(bucket, url, f"Erro inesperado: {str(e)}")
                    continue

        sep.newsBuckets()
        sep.arqClose()
        print("✅ Validação concluída.")
