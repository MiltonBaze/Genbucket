import argparse
import json
import os
import sys
import re
from modules.letters import initials
from random import randint

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

def clean_bucket_name(name):
    """
    Remove invalid characters and validate bucket name length.
    Keeps lowercase letters, numbers, and hyphens.
    Returns the cleaned name if valid, or an empty string if invalid.
    """
    name = name.lower()
    cleaned = re.sub(r'[^a-z0-9\-]', '', name)

    # Validate min and max length
    if len(cleaned) < 3 or len(cleaned) > 63:
        return ""

    # Must start and end with a letter or number
    if not (cleaned[0].isalnum() and cleaned[-1].isalnum()):
        return ""

    return cleaned

def generate_names(config: dict, prompt: str = " a \n"):
    model_name = config.get("model")
    if not model_name:
        print("❌ Model not specified in config.json")
        sys.exit(1)

    print(f"▶ Starting generation with model: {model_name}")
    model = load_model(model_name, config)

    output_dir = config.get("prompt_dir", "output")
    dataset_path = config.get("dataset_path", None)
    already_existing = set()

    if dataset_path and os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            already_existing = set(l.strip().lower() for l in f if l.strip())

    total_words = 0
    num_phases = 10

    if model_name == "lstm":
        pos = randint(0, len(initials) - 1)

    for phase in range(1, num_phases + 1):
        phase_dir = os.path.join(output_dir, f"V_{phase}")
        os.makedirs(phase_dir, exist_ok=True)
        output_txt = os.path.join(phase_dir, f"Output{phase}.txt")
        filtered_txt = os.path.join(phase_dir, f"Output{phase}_Filtered.txt")

        counter = 0
        with open(output_txt, "a", encoding="utf-8") as out, open(filtered_txt, "a", encoding="utf-8") as fil:
            while counter < 10000:
                if model_name == "lstm":
                    letter = initials[pos]
                    pos = randint(0, len(initials) - 1)
                    results = model.predict(letter, **config.get("geracao", {}))
                else:
                    results = model.predict(prompt, **config.get("geracao", {}))

                for text in results:
                    out.write(text + "\n")
                    for word in text.strip().split():
                        cleaned_word = clean_bucket_name(word)
                        if cleaned_word and cleaned_word not in already_existing:
                            fil.write(cleaned_word + "\n")
                            already_existing.add(cleaned_word)
                            counter += 1
                            total_words += 1
                            print(f"{total_words} ➜ {cleaned_word}")
                        if counter >= 10000:
                            break
                if counter >= 10000:
                    break

    print(f"✅ Generation completed. Total generated words: {total_words}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config.json file")
    parser.add_argument("--prompt", default="a \n", help="Initial prompt")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("❌ Configuration file not found.")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    generate_names(config, prompt=args.prompt)
