import os
import sys
import json
from transformers import (
    GPTNeoForCausalLM,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer
)

# === Caminhos base e config.json ===
base_path = os.path.dirname(__file__)
config_path = os.path.join(base_path, "config.json")

if not os.path.exists(config_path):
    print("❌ Arquivo 'config.json' não encontrado.")
    sys.exit(1)

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# === Verifica se dataset foi informado ===
if len(sys.argv) < 2:
    print("❌ Caminho do dataset não informado.")
    sys.exit(1)

file_path = sys.argv[1]

if not os.path.exists(file_path):
    print(f"❌ Arquivo de treinamento não encontrado: {file_path}")
    sys.exit(1)

# === Define caminhos baseados no nome do dataset ===
nome_base = os.path.splitext(os.path.basename(file_path))[0]
output_dir = os.path.join(base_path, config["treinamento_dir"], f"{nome_base}_config_json")
save_model = os.path.join(base_path, config["modelo_treinado_dir"], f"{nome_base}_config_json")

# === Verifica se o modelo já foi treinado (todos os arquivos esperados) ===
arquivos_esperados = [
    "model.safetensors",
    "training_args.bin",
    "generation_config.json",
    "config.json"
]

modelo_completo_ja_salvo = all([
    os.path.exists(os.path.join(save_model, arquivo)) for arquivo in arquivos_esperados
])

if modelo_completo_ja_salvo:
    print(f"✅ Modelo completo já treinado encontrado em: {save_model}")
    print("ℹ️  Encerrando o script (sem treinar novamente).")
    sys.exit(0)

# === Cria diretórios se necessário ===
os.makedirs(output_dir, exist_ok=True)
os.makedirs(save_model, exist_ok=True)

# === Carrega modelo e tokenizer ===
print("Carregando modelo e tokenizer...")
modelo = GPTNeoForCausalLM.from_pretrained(config["model_name"])
tokenizer = GPT2Tokenizer.from_pretrained(config["model_name"])
tokenizer.pad_token = tokenizer.eos_token

# === Prepara dataset ===
print(f"Carregando dataset: {file_path}")
dataset = TextDataset(
    tokenizer=tokenizer,
    file_path=file_path,
    block_size=config["block_size"]
)

# === Collator ===
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# === Argumentos de treinamento ===
args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    num_train_epochs=config["num_train_epochs"],
    per_device_train_batch_size=config["per_device_train_batch_size"],
    save_steps=500,
    save_total_limit=2,
    logging_dir=os.path.join(output_dir, "logs"),
    logging_steps=100
)

# === Inicia o Trainer ===
print("Iniciando treinamento...")
trainer = Trainer(
    model=modelo,
    args=args,
    data_collator=data_collator,
    train_dataset=dataset
)

trainer.train()

# === Salva modelo treinado ===
print(f"Salvando modelo treinado em: {save_model}")
trainer.save_model(save_model)

print("✅ Treinamento finalizado e modelo salvo.")
