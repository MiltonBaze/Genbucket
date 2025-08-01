import os
import json
import requests
import argparse

def validate_dataset(config: dict) -> str:
    dataset_path = config.get("dataset")
    output_folder = config.get("saida_validador", "data")

    print(" Starting dataset validation...")

    # Verifica se o caminho do dataset existe
    if not dataset_path or not os.path.exists(dataset_path):
        print(f"❌ invalid or missing dataset path: {dataset_path}")
        return ""

    print(f" Reading dataset from: {dataset_path}")

    endpoints = [
        ".s3.amazonaws.com",
        ".storage.googleapis.com",
        ".fra1.digitaloceanspaces.com",
        ".nyc3.digitaloceanspaces.com",
        ".sgp1.digitaloceanspaces.com",
        ".ams3.digitaloceanspaces.com"
    ]
    valid_buckets = []

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            bucket = line.strip()
            if not bucket:
                print(f" Line {line_number} is empty. Ignored.")
                continue

            print(f"\n Testing bucket '{bucket}' (line {line_number})...")

            for endpoint in endpoints:
                url = f"https://{bucket}{endpoint}"
                print(f"➡️  Checking  URL: {url}")

                try:
                    resp = requests.head(url, timeout=5)
                    print(f"   ↳ Response HTTP: {resp.status_code}")
                    if resp.status_code in (200, 403):
                        print(f"✅ Valid bucket found: {bucket}")
                        valid_buckets.append(bucket)
                        break  #
                    else:
                        print(f"❌ Invalid status ({resp.status_code}) para: {url}")
                except requests.RequestException as e:
                    print(f"❌ Error when accessing {url}: {e}")

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "validated_buckets.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(valid_buckets))

    print("\n✅ Validation completed.")
    print(f"✔️  Valid Buckets: {len(valid_buckets)}")
    print(f" File saved in: {output_path}")
    return output_path

# Direct execution via terminal
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=" Bucket dataset validator")
    parser.add_argument("--config", required=True, help="Path to config.json")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    validate_dataset(config)
