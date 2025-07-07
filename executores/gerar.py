# gerar.py
import json
import argparse
import os
import sys
from Letras import iniciais
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def carregar_modelo(nome_modelo: str, config: dict):
    if nome_modelo == "gpt-neo":
        from modelos.gptneo.gpt_neo_model import GPTNeoModel
        return GPTNeoModel(config)
    elif nome_modelo == "lstm":
        from modelos.lstm.lstm_model import LSTMModel
        return LSTMModel(config)
    elif nome_modelo == "transformer":
        from modelos.transformer.transformer_model import TransformerModel
        return TransformerModel(config)
    else:
        raise ValueError(f"\ Modelo desconhecido: {nome_modelo}")


def gerar_texto_por_fases(modelo, config, prompt):
    output_dir = config.get("prompt_dir", "saida")
    dataset_path = config.get("dataset_path", None)
    ja_existem = set()

    if dataset_path and os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            ja_existem = set(l.strip().lower() for l in f if l.strip())

    total_palavras = 0
    num_fases = 10

    if config["modelo"] == "lstm":
        from random import randint
        pos = randint(0, len(iniciais) - 1)

    for fase in range(1, num_fases + 1):
        fase_dir = os.path.join(output_dir, f"V_{fase}")
        os.makedirs(fase_dir, exist_ok=True)
        saida_txt = os.path.join(fase_dir, f"Saida{fase}.txt")
        filtrado_txt = os.path.join(fase_dir, f"Saida{fase}_Filtrado.txt")

        contador = 0
        with open(saida_txt, "a", encoding="utf-8") as out, open(filtrado_txt, "a", encoding="utf-8") as fil:
            while contador < 10000:
                if config["modelo"] == "lstm":
                    letra = iniciais[pos]
                    pos = randint(0, len(iniciais) - 1)
                    resultados = modelo.predict(letra, **config.get("geracao", {}))
                else:
                    resultados = modelo.predict(prompt, **config.get("geracao", {}))

                for texto in resultados:
                    out.write(texto + "\n")
                    for palavra in texto.strip().split():
                        palavra = palavra.lower()
                        if palavra and palavra not in ja_existem:
                            fil.write(palavra + "\n")
                            ja_existem.add(palavra)
                            contador += 1
                            total_palavras += 1
                            print(f"{total_palavras} --> {palavra}")
                        if contador >= 10000:
                            break
                if contador >= 10000:
                    break
    print(f"\ Geração finalizada. Total de palavras: {total_palavras}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Caminho para o arquivo config.json")
    parser.add_argument("--prompt", default="gere nomes de buckets em portugues\n", help="Prompt inicial para modelos baseados em transformers")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("\ Arquivo de configuração encontrado.")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    nome_modelo = config.get("modelo")
    if not nome_modelo:
        print("\ Modelo não especificado no config.json")
        sys.exit(1)

    print(f"\ Iniciando geração do modelo: {nome_modelo}...")
    modelo = carregar_modelo(nome_modelo, config)

    print("\ Iniciando geração de nomes de Buckets...")
    gerar_texto_por_fases(modelo, config, args.prompt)
