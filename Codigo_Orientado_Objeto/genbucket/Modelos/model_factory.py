from modelos.lstm import LSTMModel
from modelos.gptneo import GPTNeoModel
from modelos.transformer import TransformerModel

class ModelFactory:
    @staticmethod
    def criar_modelo(nome_modelo: str, dataset_path: str):
        nome = nome_modelo.upper()

        if nome == "LSTM":
            return LSTMModel(dataset_path)
        elif nome == "GPT_NEO":
            return GPTNeoModel(dataset_path)
        elif nome == "TRANSFORMER":
            return TransformerModel(dataset_path)
        else:
            raise ValueError(f"❌ Modelo '{nome_modelo}' não reconhecido.")
