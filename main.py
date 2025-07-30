import argparse
import os
import sys
import json

# Module Imports
from modules.validate_dataset import validate_dataset
from modules.training import train_model
from modules.generate import generate_names
from modules.validate import validate_names
from modules.check_buckets_public import check_buckets
from modules.analyze_content import analyze_bucket_content
from modules.analyze_vulnerabilities_v1 import analyze_vulnerabilities_1
from modules.analyze_vulnerabilities_v2 import analyze_vulnerabilities_2

def load_config(config_path):
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def execute_action(code, config):
    match code:
    
        case 1:
            validate_dataset(config)
        case 2:
            train_model(config)
        case 3:
            generate_names(config)
        case 4:
            validate_names(config)
        case 5:
            check_buckets(config)
        case 6:
            analyze_bucket_content(config)
        case 7:
            analyze_vulnerabilities_1(config)
        case 8:
            analyze_vulnerabilities_2(config)
        case 9:
            print("▶ Running full pipeline...")
            for step in range(1, 8):
                print(f"\n🔄 Step {step}...")
                execute_action(step, config)
        case _:
            print(f"❌ Invalid action code: {code}")

def main():
    parser = argparse.ArgumentParser(description="GenBucket Executor via parameters.")
    parser.add_argument("--acao", type=int, required=True, help="Action code to execute (1–9)")
    parser.add_argument("--config", type=str, required=True, help="Path to the config.json file")
    args = parser.parse_args()

    config = load_config(args.config)
    execute_action(args.acao, config)

if __name__ == "__main__":
    main()
