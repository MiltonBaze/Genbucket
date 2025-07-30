import os
import json
import argparse
import requests
import sys
import modules.BucketSeparator as sep

def validate_names(config):
    model = config.get("model")
    versions_config = config.get("validar_versoes", "all")

    prompt_dir = os.path.join("result", model, "prompts")
    catalog_dir = os.path.join("result", model, "cataloged")

    if versions_config == "all":
        versions = list(range(1, 11))  # V1 to V10
    else:
        versions = versions_config if isinstance(versions_config, list) else [versions_config]

    for version in versions:
        filtered_file = os.path.join(prompt_dir, f"V_{version}", f"Output{version}_Filtered.txt")
        catalog_version_dir = os.path.join(catalog_dir, f"V_{version}")
        os.makedirs(catalog_version_dir, exist_ok=True)

        sep.output_mode = "a"
        sep.output_dir = catalog_version_dir + "/"
        sep.init()

        if not os.path.exists(filtered_file):
            print(f"❌ Filtered bucket file not found: {filtered_file}")
            continue

        endpoints = [
            ".s3.amazonaws.com",
            ".storage.googleapis.com",
            ".fra1.digitaloceanspaces.com",
            ".nyc3.digitaloceanspaces.com",
            ".sgp1.digitaloceanspaces.com",
            ".ams3.digitaloceanspaces.com"
        ]

        with open(filtered_file, "r", encoding="utf-8") as f:
            for i, bucket in enumerate(f, start=1):
                bucket = bucket.strip()
                if not bucket:
                    continue

                try:
                    for endpoint in endpoints:
                        url = f"https://{bucket}{endpoint}"
                        try:
                            response = requests.head(url, timeout=10)
                            status = response.status_code
                        except requests.exceptions.RequestException as e:
                            sep.outros(bucket, url, f"Network error: {str(e)}")
                            continue

                        if status == 200:
                            sep.register_public(bucket, url)
                        elif status == 403:
                            sep.register_private(bucket, url)
                        elif status == 404:
                            sep.register_not_found(bucket, url)
                        elif status == 400:
                            sep.register_other(bucket, url, "Invalid bucket name")
                        else:
                            sep.register_other(bucket, url, status)

                        print(f"{i} - {bucket} - {status} - {url}")

                except KeyboardInterrupt:
                    print("❌ Execution interrupted by user.")
                    break
                except Exception as e:
                    sep.register_other(bucket, url, f"Erro inesperado: {str(e)}")
                    continue

        sep.write_unique_buckets()
        sep.close_all_files()
        print(f"✅ Validation for version {version} completed.\n")


# Direct CLI execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validator for generated names (buckets).")
    parser.add_argument("--config", required=True, help="Path to config.json file")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    validate_names(config)
