import requests

class BucketValidator:
    def __init__(self):
        self.endpoints = [
            '.s3.amazonaws.com',
            '.storage.googleapis.com',
            '.fra1.digitaloceanspaces.com',
            '.nyc3.digitaloceanspaces.com',
            '.sgp1.digitaloceanspaces.com',
            '.ams3.digitaloceanspaces.com'
        ]

    def validar(self, caminho: str) -> list:
        buckets_validos = []

        with open(caminho, "r", encoding="utf-8") as f:
            linhas = f.readlines()

        for linha in linhas:
            bucket = linha.strip()
            for endpoint in self.endpoints:
                url = f"https://{bucket}{endpoint}"
                try:
                    response = requests.head(url, timeout=3)
                    status = response.status_code

                    if status in [200, 403]:
                        print(f"[✔] Bucket encontrado: {bucket} ({status}) - {url}")
                        buckets_validos.append(bucket)
                        break
                    elif status == 404:
                        print(f"[✖] Não encontrado: {bucket}")
                    elif status == 400:
                        print(f"[!] Nome inválido: {bucket}")
                    else:
                        print(f"[?] Status {status} para {bucket}")
                except Exception as e:
                    print(f"[!] Erro ao verificar {bucket}: {e}")
        return buckets_validos
