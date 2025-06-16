import os
import json
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

def gerar_buckets(dataset_path, config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Arquivo de configuração não encontrado: {config_path}")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"❌ Dataset não encontrado: {dataset_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    base_de_dados = os.path.splitext(os.path.basename(dataset_path))[0]
    base_path = os.path.dirname(config_path)

    prompt_base_dir = os.path.join(base_path, config["prompt_dir"])
    modelo_path = os.path.join(base_path, config["modelo_treinado_dir"], f"{base_de_dados}_config_json")

    if not os.path.exists(modelo_path):
        raise FileNotFoundError(f"❌ Modelo treinado não encontrado: {modelo_path}")

    os.makedirs(prompt_base_dir, exist_ok=True)

    print("🔄 Carregando modelo e tokenizer...")
    model = GPTNeoForCausalLM.from_pretrained(modelo_path)
    tokenizer = GPT2Tokenizer.from_pretrained(config["model_name"])
    tokenizer.pad_token = tokenizer.eos_token

    with open(dataset_path, 'r', encoding='utf-8') as f:
        base_de_treinamento = [linha.strip() for linha in f.readlines()]

    for fase in range(1, 11):
        fase_dir = os.path.join(prompt_base_dir, f'V_{fase}')
        os.makedirs(fase_dir, exist_ok=True)

        saida_arquivo = os.path.join(fase_dir, f'Saida{fase}.txt')
        saida_filtrada_arquivo = os.path.join(fase_dir, f'Saida{fase}_Filtrado.txt')

        ja_existem = set(base_de_treinamento)
        contador = 0
        prompt = "gere chave de buckets em portugues\n"

        print(f"🚀 Gerando nomes para a fase {fase}...")

        while contador < 10000:
            input_ids = tokenizer.encode(prompt, return_tensors="pt")
            outputs = model.generate(
                input_ids,
                max_length=32,
                num_return_sequences=3,
                no_repeat_ngram_size=2,
                do_sample=True,
                top_k=1000,
                top_p=0.85,
                temperature=1.0
            )

            for sequence in outputs:
                texto_gerado = tokenizer.decode(sequence, skip_special_tokens=True)
                texto_limpo = texto_gerado.replace(prompt.strip(), "").strip()

                if not texto_limpo:
                    continue

                with open(saida_arquivo, 'a', encoding='utf-8') as f:
                    f.write(texto_limpo + '\n')

                for palavra in texto_limpo.split():
                    palavra = palavra.strip().lower()
                    if palavra and palavra not in ja_existem:
                        ja_existem.add(palavra)
                        with open(saida_filtrada_arquivo, 'a', encoding='utf-8') as f:
                            f.write(palavra + '\n')
                        print(f'{contador} --> {palavra}')
                        contador += 1

                        if contador >= 10000:
                            break

            if contador >= 10000:
                break

    print("✅ Geração concluída.")
