import os
import sys
import json
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

# === Carrega configuração do JSON de forma segura ===
base_path = os.path.dirname(__file__)
config_path = os.path.join(base_path, "config.json")

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
    
# === Verifica se o dataset foi passado ===
if len(sys.argv) < 2:
    print("❌ Caminho do dataset não informado.")
    sys.exit(1)

file_path = sys.argv[1]

if not os.path.exists(file_path):
    print(f"❌ Arquivo de entrada não encontrado: {file_path}")
    sys.exit(1)

# === Caminhos dinâmicos ===
base_de_dados = os.path.splitext(os.path.basename(file_path))[0]
base_path = os.path.dirname(__file__)
prompt_base_dir = os.path.join(base_path, config["prompt_dir"])
os.makedirs(prompt_base_dir, exist_ok=True)

# === Carrega modelo e tokenizer ===
modelo_path = os.path.join(base_path, config["modelo_treinado_dir"], f"{base_de_dados}_config_json")
if not os.path.exists(modelo_path):
    print(f"❌ Modelo não encontrado em: {modelo_path}")
    sys.exit(1)

print(" Carregando modelo e tokenizer...")
model = GPTNeoForCausalLM.from_pretrained(modelo_path)
tokenizer = GPT2Tokenizer.from_pretrained(config["model_name"])
tokenizer.pad_token = tokenizer.eos_token

# === Carrega dados do dataset ===
with open(file_path, 'r', encoding='utf-8') as f:
    base_de_treinamento = [linha.strip() for linha in f.readlines()]

# === Geração de nomes por fase ===
for fase in range(1, 11):
    fase_dir = os.path.join(prompt_base_dir, f'V_{fase}')
    os.makedirs(fase_dir, exist_ok=True)

    saida_arquivo = os.path.join(fase_dir, f'Saida{fase}.txt')
    saida_filtrada_arquivo = os.path.join(fase_dir, f'Saida{fase}_Filtrado.txt')

    # Inicializa conjunto de nomes já gerados
    ja_existem = set(base_de_treinamento)
    contador = 0
    prompt = "gere chave de buckets em portugues\n"

    print(f" Gerando nomes para a fase {fase}...")

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

            if texto_gerado.startswith(prompt.strip()):
                texto_limpo = texto_gerado[len(prompt.strip()):].strip()
            else:
                texto_limpo = texto_gerado.strip()

            if not texto_limpo:
                continue

            # Salva nome gerado
            with open(saida_arquivo, 'a', encoding='utf-8') as f:
                f.write(texto_limpo + '\n')

            # Filtra e salva nomes únicos
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
