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
    print(f"❌ Arquivo de treinamento não encontrado: {file_path}")
    sys.exit(1)

# === Caminhos dinâmicos ===
base_de_dados = os.path.splitext(os.path.basename(file_path))[0]
base_path = os.path.dirname(__file__)
output_dir = os.path.join(base_path, config["treinamento_dir"], f"{base_de_dados}_config_json")
save_model = os.path.join(base_path, config["modelo_treinado_dir"], f"{base_de_dados}_config_json")

# === Cria diretórios se necessário ===
os.makedirs(output_dir, exist_ok=True)
os.makedirs(save_model, exist_ok=True)

# === Modelo e Tokenizer ===
print(" Carregando modelo e tokenizer...")
modelo = GPTNeoForCausalLM.from_pretrained(config["model_name"])
tokenizer = GPT2Tokenizer.from_pretrained(config["model_name"])
tokenizer.pad_token = tokenizer.eos_token

# === Dataset ===
print(f" Carregando dataset: {file_path}")
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

# === Argumentos de treino ===
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

# === Trainer ===
print(" Iniciando treinamento...")
trainer = Trainer(
    model=modelo,
    args=args,
    data_collator=data_collator,
    train_dataset=dataset
)

trainer.train()

# === Salva modelo ===
print(f"💾 Salvando modelo treinado em: {save_model}")
trainer.save_model(save_model)
