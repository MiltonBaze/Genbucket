from modelos.base_model import BaseModel
from transformers import (
    GPTNeoForCausalLM,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer
)
import torch
import os

class GPTNeoModel(BaseModel):
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.tokenizer = None

        self.model_name = config.get("model_name", "EleutherAI/gpt-neo-125M")
        self.modelo_treinado_dir = config.get("modelo_treinado_dir", "resultados/gptneo/modelos_treinados")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Tenta carregar modelo já treinado, se existir
        if os.path.exists(self.modelo_treinado_dir):
            try:
                self.tokenizer = GPT2Tokenizer.from_pretrained(self.modelo_treinado_dir)
                self.model = GPTNeoForCausalLM.from_pretrained(self.modelo_treinado_dir).to(self.device)
            except Exception:
                # fallback para pré-treinado se falhar
                self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
                self.model = GPTNeoForCausalLM.from_pretrained(self.model_name).to(self.device)
        else:
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.model = GPTNeoForCausalLM.from_pretrained(self.model_name).to(self.device)

        self.tokenizer.pad_token = self.tokenizer.eos_token

    def fit(self, dataset_path: str):
        model_name = self.config.get("model_name", "EleutherAI/gpt-neo-125M")
        block_size = self.config.get("block_size", 128)
        num_train_epochs = self.config.get("epochs", 200)
        batch_size = self.config.get("batch_size", 4)

        treinamento_dir = self.config.get("treinamento_dir", "resultados/gptneo/treinamento")
        modelo_treinado_dir = self.config.get("modelo_treinado_dir", "resultados/gptneo/modelos_treinados")

        nome_base = os.path.splitext(os.path.basename(dataset_path))[0]
        output_dir = os.path.join(treinamento_dir, f"{nome_base}_treino")
        save_model = os.path.join(modelo_treinado_dir, f"{nome_base}_modelo")

        arquivos_esperados = [
            "pytorch_model.bin", "training_args.bin", "config.json"
        ]

        if all(os.path.exists(os.path.join(save_model, f)) for f in arquivos_esperados):
            print(f"✅ Modelo já treinado encontrado em {save_model}. Ignorando novo treinamento.")
            return

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(save_model, exist_ok=True)

        print(" Carregando modelo e tokenizer...")
        model = GPTNeoForCausalLM.from_pretrained(model_name)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        print(f" Carregando dataset: {dataset_path}")
        dataset = TextDataset(
            tokenizer=tokenizer,
            file_path=dataset_path,
            block_size=block_size
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer, mlm=False
        )

        args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=500,
            save_total_limit=2,
            logging_dir=os.path.join(output_dir, "logs"),
            logging_steps=100
        )

        print(" Iniciando treinamento...")
        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=dataset,
            data_collator=data_collator
        )
        trainer.train()

        print(f" Salvando modelo treinado em: {save_model}")
        trainer.save_model(save_model)
        print("✅ Treinamento finalizado com sucesso.")

    def predict(self, prompt: str, **kwargs):
        max_length = kwargs.get("max_length", 50)
        num_return_sequences = kwargs.get("num_return_sequences", 1)
        temperature = kwargs.get("temperature", 1.0)
        top_k = kwargs.get("top_k", 50)
        top_p = kwargs.get("top_p", 0.95)

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)

        outputs = self.model.generate(
            input_ids,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
        )

        return [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    
    def validar_buckets(self, prompt_dir, catalogados_dir, versao):
        print("⚠️ Método validar_buckets() ainda não implementado para GPTNeoModel.")
        # Pode ser implementado futuramente se necessário

    def verificar_buckets_publicos(self, config):
        print("⚠️ Método verificar_buckets_publicos() ainda não implementado para GPTNeoModel.")
        # Pode ser implementado futuramente se necessário

    def analise_conteudo(self):
        from executores.analise_conteudo import executar_analise_conteudo
        executar_analise_conteudo(self)