import os
from genbucket.modelos.base import Modelo
from GenBucket.GPT_neo.treinamento import treinar_modelo
from GenBucket.GPT_neo.gerador import gerar_buckets 
from GenBucket.GPT_neo.validador import ValidadorBucketsGPTNeo
from GenBucket.GPT_neo.verificador import VerificadorBucketsPublicos
from GenBucket.GPT_neo.verificador_vulnerabilidades import VerificadorVulnerabilidades

class GPTNeoModel(Modelo):
    def __init__(self, dataset_path, config_path=None):
        super().__init__(dataset_path)
        self.config_path = config_path

    def treinar(self):
        print("📚 Iniciando treinamento do modelo GPT-Neo...")
        treinar_modelo(self.dataset_path, self.config_path)

    def gerar(self):
        print("🧠 Gerando buckets com GPT-Neo...")
        gerar_buckets(self.dataset_path, self.config_path)

    def validar(self):
        print("🔍 Validando buckets com GPT-Neo...")
        validador = ValidadorBucketsGPTNeo(self.config_path)
        validador.validar()

    def analisar(self):
        print("📂 Analisando buckets públicos...")
        verificador = VerificadorBucketsPublicos(self.config_path)
        verificador.verificar()

    def analisar_vulnerabilidades(self):
        print("🛡️ Executando análise de vulnerabilidades...")
        verificador = VerificadorVulnerabilidades(
            base_dir=os.path.join(os.path.dirname(__file__), "..", "GPT_neo")
        )
        verificador.analisar_todos()
