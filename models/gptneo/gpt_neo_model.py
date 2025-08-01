from models.base_model import BaseModel
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
        self.trained_model_dir = config.get("trained_model_dir", "result/gptneo/model_training")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if os.path.exists(self.trained_model_dir):
            try:
                self.tokenizer = GPT2Tokenizer.from_pretrained(self.trained_model_dir)
                self.model = GPTNeoForCausalLM.from_pretrained(self.trained_model_dir).to(self.device)
            except Exception:
                self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
                self.model = GPTNeoForCausalLM.from_pretrained(self.model_name).to(self.device)
        else:
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.model = GPTNeoForCausalLM.from_pretrained(self.model_name).to(self.device)

        self.tokenizer.pad_token = self.tokenizer.eos_token

    def prepare_char_dataset(self, input_path, output_path):
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        tokenized_lines = []
        for line in lines:
            line = line.strip().lower()
            if line:
                tokenized = " ".join(list(line))
                tokenized_lines.append(tokenized)

        with open(output_path, "w", encoding="utf-8") as f:
            for line in tokenized_lines:
                f.write(line + "\n")

    def fit(self, dataset_path: str):
        model_name = self.config.get("model_name", "EleutherAI/gpt-neo-125M")
        block_size = self.config.get("block_size", 128)
        num_train_epochs = self.config.get("epochs", 5)
        batch_size = self.config.get("batch_size", 4)

        training_dir = self.config.get("training_dir", "result/gptneo/training")
        trained_model_dir = self.config.get("trained_model_dir", "result/gptneo/trained_models")

        base_name = os.path.splitext(os.path.basename(dataset_path))[0]
        output_dir = os.path.join(training_dir, f"{base_name}_train")
        save_model_path = os.path.join(trained_model_dir, f"{base_name}_model")
        char_dataset_path = os.path.join(output_dir, "char_dataset.txt")

        expected_files = ["pytorch_model.bin", "training_args.bin", "config.json"]
        if all(os.path.exists(os.path.join(save_model_path, f)) for f in expected_files):
            print(f"✅ Trained model already found at {save_model_path}. Skipping training.")
            return

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(save_model_path, exist_ok=True)

        print(" Preprocessing dataset by character...")
        self.prepare_char_dataset(dataset_path, char_dataset_path)

        print(" Loading model and tokenizer...")
        model = GPTNeoForCausalLM.from_pretrained(model_name)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        print(f" Loading dataset: {char_dataset_path}")
        dataset = TextDataset(
            tokenizer=tokenizer,
            file_path=char_dataset_path,
            block_size=block_size
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
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

        print(" Starting training...")
        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=dataset,
            data_collator=data_collator
        )
        trainer.train()

        print(f" Saving trained model at: {save_model_path}")
        trainer.save_model(save_model_path)
        print("✅ Training completed successfully.")

    def predict(self, prompt: str, **kwargs):
        max_length = kwargs.get("max_length", 20)
        num_return_sequences = kwargs.get("num_return_sequences", 3)
        temperature = kwargs.get("temperature", 0.8)
        top_k = kwargs.get("top_k", 50)
        top_p = kwargs.get("top_p", 0.95)

        # Character-level tokenization
        prompt = " ".join(list(prompt.strip().lower()))
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)

        outputs = self.model.generate(
            input_ids,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            pad_token_id=self.tokenizer.eos_token_id
        )

        results = []
        for output in outputs:
            generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
            cleaned_text = generated_text.replace(" ", "").strip()
            results.append(cleaned_text)

        return results
