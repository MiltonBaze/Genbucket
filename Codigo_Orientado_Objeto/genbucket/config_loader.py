import json
import os
import sys

class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load(self):
        if not os.path.exists(self.config_path):
            print(f"❌ Arquivo de configuração '{self.config_path}' não encontrado.")
            sys.exit(1)

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler o JSON: {e}")
            sys.exit(1)
