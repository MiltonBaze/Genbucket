# training.py
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_model(model_name: str, config: dict):
    if model_name == "gptneo":
        from models.gptneo.gpt_neo_model import GPTNeoModel
        return GPTNeoModel(config)
    elif model_name == "lstm":
        from models.lstm.lstm_model import LSTMModel
        return LSTMModel(config)
    elif model_name == "transformer":
        from models.transformer.transformer_model import TransformerModel
        return TransformerModel(config)
    else:
        raise ValueError(f"❌ Unknown model: {model_name}")

def train_model(config: dict):
    dataset_path = config.get("dataset")

    if not dataset_path or not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return

    model_name = config.get("model")
    if not model_name:
        print("❌ Model not specified in config.json.")
        return

    print(f" Starting training for model: {model_name}")
    model = load_model(model_name, config)
    model.fit(dataset_path)
    print("✅ Training completed successfully.")

# Command-line execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Language model training")
    parser.add_argument("--config", required=True, help="Path to config.json")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    train_model(config)
