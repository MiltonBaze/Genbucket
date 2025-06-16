import os
import json
from transformers import (
    GPTNeoForCausalLM,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer
)

def treinar_modelo(dataset_path, config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Arquivo de configuração não encontrado: {config_path}")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"❌ Dataset não encontrado: {dataset_path}")

    # Carrega config
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    base_path = os.path.dirname(config_path)
    nome_base = os.path.splitext(os.path.basename(dataset_path))[0]
    output_dir = os.path.join(base_path, config["treinamento_dir"], f"{nome_base}_config_json")
    save_model = os.path.join(base_path, config["modelo_treinado_dir"], f"{nome_base}_config_json")

    # Verifica se o modelo já está treinado
    arquivos_esperados = [
        "model.safetensors",
        "training_args.bin",
        "generation_config.json",
        "config.json"
    ]

    if all([os.path.exists(os.path.join(save_model, a)) for a in arquivos_esperados]):
        print(f"✅ Modelo completo já treinado encontrado em: {save_model}")
        print("ℹ️  Ignorando novo treinamento.")
        return

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(save_model, exist_ok=True)

    print("Carregando modelo e tokenizer...")
    modelo = GPTNeoForCausalLM.from_pretrained(config["model_name"])
    tokenizer = GPT2Tokenizer.from_pretrained(config["model_name"])
    tokenizer.pad_token = tokenizer.eos_token

    print(f"Carregando dataset: {dataset_path}")
    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=dataset_path,
        block_size=config["block_size"]
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

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

    print("Iniciando treinamento...")
    trainer = Trainer(
        model=modelo,
        args=args,
        data_collator=data_collator,
        train_dataset=dataset
    )

    trainer.train()

    print(f"Salvando modelo treinado em: {save_model}")
    trainer.save_model(save_model)
    print("✅ Treinamento finalizado com sucesso.")
