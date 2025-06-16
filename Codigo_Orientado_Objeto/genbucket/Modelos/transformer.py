import os
from modelos.base import Modelo
from GenBucket.Transformer.transformer import TransformerModel
# from GenBucket.TRANSFORMER.gerador import gerar_buckets_transformer
# from GenBucket.TRANSFORMER.validador import ValidadorBucketsTransformer
# from GenBucket.TRANSFORMER.verificador import VerificadorBucketsPublicosTransformer
# from GenBucket.TRANSFORMER.verificador_vulnerabilidades import VerificadorVulnerabilidadesTransformer


class TransformerModelWrapper(Modelo):
    def __init__(self, dataset_path, config_path=None):
        super().__init__(dataset_path)
        self.config_path = config_path
        self.generator = TransformerModel(dataset_path, config_path)

    def treinar(self):
        print("📚 Iniciando treinamento do modelo Transformer...")
        self.generator.train()

    def gerar(self):
        print("🧠 Gerando buckets com Transformer...")
        self.generator.generate()

    def validar(self):
        print("🔍 Validação ainda não implementada para Transformer.")
        # TODO: Implementar como nos outros modelos

    def analisar(self):
        print("📂 Análise pública ainda não implementada para Transformer.")
        # TODO: Implementar como nos outros modelos

    def analisar_vulnerabilidades(self):
        print("🛡️ Análise de vulnerabilidades ainda não implementada para Transformer.")
        # TODO: Implementar como nos outros modelos
   
