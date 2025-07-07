# validar_dataset.py

import os
import requests
import argparse

class ValidadorDataset:
    def __init__(self, dataset_path: str, pasta_saida: str = "dados"):
        self.dataset_path = dataset_path
        self.pasta_saida = pasta_saida
        self.endpoints = [
            ".s3.amazonaws.com",
            ".storage.googleapis.com",
            ".fra1.digitaloceanspaces.com",
            ".nyc3.digitaloceanspaces.com",
            ".sgp1.digitaloceanspaces.com",
            ".ams3.digitaloceanspaces.com"
        ]

    def validar(self) -> str:
        if not os.path.exists(self.dataset_path):
            print(f"❌ Arquivo não encontrado: {self.dataset_path}")
            return self.dataset_path

        print(f"🔎 Validando dataset em: {self.dataset_path}")
        buckets_validos = []

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            for linha in f:
                bucket = linha.strip()
                if not bucket:
                    continue

                for endpoint in self.endpoints:
                    url = f"https://{bucket}{endpoint}"
                    try:
                        resp = requests.head(url, timeout=5)
                        if resp.status_code in (200, 403):
                            buckets_validos.append(bucket)
                            break
                    except requests.RequestException:
                        continue

        os.makedirs(self.pasta_saida, exist_ok=True)
        saida_path = os.path.join(self.pasta_saida, "buckets_validado.txt")

        with open(saida_path, "w", encoding="utf-8") as f:
            f.write("\n".join(buckets_validos))

        print(f"✅ Dataset validado com {len(buckets_validos)} buckets.")
        print(f"📝 Arquivo salvo em: {saida_path}")
        return saida_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Valida um dataset de buckets.")
    parser.add_argument("dataset", help="Caminho para o arquivo de entrada (ex: dados/buckets.txt)")
    parser.add_argument("--saida", help="Pasta de saída (default: dados)", default="dados")
    args = parser.parse_args()

    validador = ValidadorDataset(args.dataset, args.saida)
    validador.validar()
