import os
import subprocess

class ModelExecutor:
    def __init__(self):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "GenBucket"))

        self.scripts = {
            "LSTM": os.path.join(self.base_path, "LSTM", "LSTM.py"),
            "LSTM_VALIDACAO": os.path.join(self.base_path, "LSTM", "validador_buckets.py"),
            "LSTM_VERIFICACAO": os.path.join(self.base_path, "LSTM", "verificadorBucketspublicos.py"),
            "LSTM_ANALISA_PUBLICOS": os.path.join(self.base_path, "LSTM", "Analisa_Publico.py"),
            "LSTM_ANALISE_FERRAMENTAS": os.path.join(self.base_path, "LSTM", "Analise_Vulnerabilidades.py"),

            "GPT_NEO_TREINAMENTO": os.path.join(self.base_path, "GPT_neo", "Treinamento.py"),
            "GPT_NEO_GERADOR": os.path.join(self.base_path, "GPT_neo", "GPT_Gerador.py"),
            "GPT_NEO_VALIDACAO": os.path.join(self.base_path, "GPT_neo", "validador_buckets.py"),
            "GPT_NEO_VERIFICACAO": os.path.join(self.base_path, "GPT_neo", "verificadorBucketspublicos.py"),
            "GPT_NEO_ANALISA_PUBLICOS": os.path.join(self.base_path, "GPT_neo", "Analisa_Publico.py"),
            "GPT_NEO_ANALISE_FERRAMENTAS": os.path.join(self.base_path, "GPT_neo", "Analise_Vulnerabilidades.py"),

            "TRANSFORMER": os.path.join(self.base_path, "TRANSFORMER", "transformer.py"),
            "TRANSFORMER_VALIDACAO": os.path.join(self.base_path, "TRANSFORMER", "validador_buckets.py"),
            "TRANSFORMER_VERIFICACAO": os.path.join(self.base_path, "TRANSFORMER", "verificadorBucketspublicos.py"),
            "TRANSFORMER_ANALISA_PUBLICOS": os.path.join(self.base_path, "TRANSFORMER", "Analisa_Publico.py"),
            "TRANSFORMER_ANALISE_FERRAMENTAS": os.path.join(self.base_path, "TRANSFORMER", "Analise_Vulnerabilidades.py"),
        }

    def _executar_script(self, script_path, *args):
        try:
            print(f"▶️ Executando: {script_path}")
            subprocess.run(["python", script_path, *args], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar {script_path}: {e}")

    def _executar_validador_e_verificador(self, validador, verificador):
        self._executar_script(validador)
        self._executar_script(verificador)

    def _executar_analises(self, publico, vulnerabilidades):
        self._executar_script(publico)
        self._executar_script(vulnerabilidades)

    def executar(self, modelo: str, dataset_path: str) -> bool:
        try:
            if modelo == "GPT_NEO":
                self._executar_script(self.scripts["GPT_NEO_TREINAMENTO"], dataset_path)
                self._executar_script(self.scripts["GPT_NEO_GERADOR"], dataset_path)
                self._executar_validador_e_verificador(
                    self.scripts["GPT_NEO_VALIDACAO"], self.scripts["GPT_NEO_VERIFICACAO"]
                )
                self._executar_analises(
                    self.scripts["GPT_NEO_ANALISA_PUBLICOS"], self.scripts["GPT_NEO_ANALISE_FERRAMENTAS"]
                )

            elif modelo == "LSTM":
                self._executar_script(self.scripts["LSTM"], dataset_path)
                self._executar_validador_e_verificador(
                    self.scripts["LSTM_VALIDACAO"], self.scripts["LSTM_VERIFICACAO"]
                )
                self._executar_analises(
                    self.scripts["LSTM_ANALISA_PUBLICOS"], self.scripts["LSTM_ANALISE_FERRAMENTAS"]
                )

            elif modelo == "TRANSFORMER":
                self._executar_script(self.scripts["TRANSFORMER"], dataset_path)
                self._executar_validador_e_verificador(
                    self.scripts["TRANSFORMER_VALIDACAO"], self.scripts["TRANSFORMER_VERIFICACAO"]
                )
                self._executar_analises(
                    self.scripts["TRANSFORMER_ANALISA_PUBLICOS"], self.scripts["TRANSFORMER_ANALISE_FERRAMENTAS"]
                )

            else:
                print(f"❌ Modelo '{modelo}' não reconhecido.")
                return False

            print(f"✅ Execução do modelo '{modelo}' concluída com sucesso.")
            return True

        except subprocess.CalledProcessError:
            print(f"❌ Falha durante a execução do modelo '{modelo}'.")
            return False
