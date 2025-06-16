import os
from modelos.base import Modelo

from GenBucket.LSTM.gerador import LSTMModel as GeradorLSTM
from GenBucket.LSTM.validador import ValidadorBucketsLSTM
from GenBucket.LSTM.verificador import VerificadorBucketsPublicosLSTM
from GenBucket.LSTM.verificador_vulnerabilidades import VerificadorVulnerabilidadesLSTM


class LSTMModel(Modelo):
    def __init__(self, dataset_path, config_path=None):
        super().__init__(dataset_path)
        self.config_path = config_path
        self.gerador = GeradorLSTM(dataset_path, config_path)
	self.validador = ValidadorBucketsLSTM()
        self.verificador = VerificadorBucketsPublicosLSTM()
        self.verificador_vuln = VerificadorVulnerabilidadesLSTM(
            base_dir=os.path.join(os.path.dirname(__file__), "..", "LSTM")
        )

    def treinar(self):
        print("📚 Iniciando treinamento do modelo LSTM...")
        self.gerador.treinar()

    def gerar(self):
        print("🧠 Gerando buckets com LSTM...")
        self.gerador.gerar()

    def validar(self):
        print("🔍 Validando buckets com LSTM...")
        self.validador.validar()

    def analisar(self):
        print("📂 Analisando buckets públicos com LSTM...")
       self.verificador.verificar()

    def analisar_vulnerabilidades(self):
        print("🛡️ Executando análise de vulnerabilidades com LSTM...")
         self.verificador_vuln.analisar_todos()
