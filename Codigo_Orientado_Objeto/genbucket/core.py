import os
from GenBucket.config_loader import ConfigLoader
from GenBucket.file_manager import FileManager
from GenBucket.bucket_validator import BucketValidator
from GenBucket.model_executor import ModelExecutor


class GenBucket:
    def __init__(self, config_path: str):
        # Carrega a configuração a partir do JSON
        self.config = ConfigLoader(config_path).load()
        self.dataset_path = self.config.get("dataset_path")
        self.modelo = self.config.get("modelo")
        self.validar_buckets = self.config.get("validar_buckets", False)

        # Arquivos padrão
        self.arquivo_gerados = "buckets_gerados.txt"
        self.arquivo_validados = "buckets_validados.txt"

        # Instâncias dos componentes
        self.validador = BucketValidator()
        self.executor = ModelExecutor()

    def executar(self):
        if not self.dataset_path or not self.modelo:
            print("❌ Você precisa fornecer 'dataset_path' e 'modelo' no JSON.")
            return

        # Verifica se o dataset é válido
        if not self.validador.verificar_dataset_valido(self.dataset_path):
            print(f"❌ Dataset inválido ou extensão não suportada: {self.dataset_path}")
            return

        print(f"✅ Dataset: {self.dataset_path}")
        print(f"✅ Modelo: {self.modelo}")

        # Valida os buckets do dataset
        if self.validar_buckets:
            print("🔍 Validando buckets...")
            buckets_validos = self.validador.validar(self.dataset_path)
            FileManager.salvar_em_arquivo(self.arquivo_validados, buckets_validos)
            print(f"✅ {len(buckets_validos)} buckets válidos salvos em '{self.arquivo_validados}'")

        # Executa o modelo correspondente
        print(f"\n🚀 Executando modelo '{self.modelo}' com dataset '{self.dataset_path}'...")
        self.executor.executar(self.modelo, self.dataset_path)

        # Verifica se os buckets foram gerados
        if FileManager.arquivo_existe(self.arquivo_gerados):
            print(f"\n✅ Buckets gerados foram salvos em: {self.arquivo_gerados}")
        else:
            print("\n⚠️ Nenhum bucket gerado foi encontrado.")
