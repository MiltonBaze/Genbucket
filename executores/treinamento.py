# treinamento.py
import json
import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def carregar_modelo(nome_modelo: str, config: dict):
    if nome_modelo == "gptneo":
        from modelos.gptneo.gpt_neo_model import GPTNeoModel
        return GPTNeoModel(config)
    elif nome_modelo == "lstm":
        from modelos.lstm.lstm_model import LSTMModel
        return LSTMModel(config)
    elif nome_modelo == "transformer":
        from modelos.transformer.transformer_model import TransformerModel
        return TransformerModel(config)
    else:
        raise ValueError(f" Modelo desconhecido: {nome_modelo}")


def main():
    parser = argparse.ArgumentParser(description="Treinamento dos modelos de linguagem")
    parser.add_argument("--config", required=True, help="Caminho para o arquivo config.json")
    parser.add_argument("--dataset", required=True, help="Caminho para o arquivo de texto de treinamento")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f" Arquivo de configuração encontrado: {args.config}")
        sys.exit(1)

    if not os.path.exists(args.dataset):
        print(f"Arquivo de dataset não encontrado: {args.dataset}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    nome_modelo = config.get("modelo")
    if not nome_modelo:
        print("Modelo não especificado no config.json.")
        sys.exit(1)

    print(f" Iniciando treinamento do modelo: {nome_modelo}")
    modelo = carregar_modelo(nome_modelo, config)
    modelo.fit(args.dataset)
    print(" Treinamento concluido com sucesso.")


if __name__ == "__main__":
    main()
