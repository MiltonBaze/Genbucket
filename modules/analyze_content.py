import os
import sys
import json
import re
import argparse
from urllib.parse import urlparse
from collections import defaultdict, Counter


def analyze_bucket_content(config):
    catalog_dir = config.get("catalogados_dir")
    model_name = config.get("model", "unknown")

    print(f"🔍 Starting bucket content analysis ({model_name})...")

    desired_extensions = {
        "js", "mjs", "cjs", "jsx", "ts", "tsx", "xml",
        "json", "html", "php", "asp", "aspx", "jsp", "svg"
    }

    if not catalog_dir or not os.path.isdir(catalog_dir):
        print(f"❌ Directory not found: {catalog_dir}")
        return

    for version_name in sorted(os.listdir(catalog_dir)):
        version_path = os.path.join(catalog_dir, version_name)
        public_content_path = os.path.join(version_path, "PublicContent")

        if not (os.path.isdir(public_content_path) and version_name.lower().startswith("v_")):
            continue

        version_number = version_name.lower().replace("v_", "")
        result_folder = os.path.join(version_path, f"AnalysisResult_V{version_number}")
        os.makedirs(result_folder, exist_ok=True)

        summary_file = os.path.join(result_folder, "extensions_count.txt")
        bucket_file = os.path.join(result_folder, "buckets.txt")
        extension_file = os.path.join(result_folder, "extensions_general.txt")

        count_by_extension = defaultdict(int)
        bucket_data = defaultdict(lambda: defaultdict(int))
        all_extensions_count = Counter()

        for file_name in os.listdir(public_content_path):
            if not file_name.endswith(".txt"):
                continue

            file_path = os.path.join(public_content_path, file_name)
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if "http" not in line:
                        continue

                    match = re.search(r'(https?://[^\s>]+)', line)
                    if not match:
                        continue

                    url = match.group(1)
                    url_path = urlparse(url).path
                    file_from_url = os.path.basename(url_path)

                    if "." not in file_from_url:
                        continue

                    _, ext = os.path.splitext(file_from_url)
                    ext = ext[1:].lower()
                    all_extensions_count[ext] += 1

                    if ext in desired_extensions:
                        count_by_extension[ext] += 1
                        host = urlparse(url).netloc

                        if "s3" in host:
                            provider = "s3"
                        elif "storage" in host:
                            provider = "google"
                        elif "digitaloceanspaces" in host:
                            provider = "digitalocean"
                        else:
                            provider = "unknown"

                        bucket_data[(host, provider)][ext] += 1

        with open(summary_file, "w", encoding="utf-8") as f:
            for ext in sorted(count_by_extension.keys()):
                f.write(f"{ext}: {count_by_extension[ext]} files\n")

        with open(bucket_file, "w", encoding="utf-8") as f:
            for (bucket, provider), data in bucket_data.items():
                f.write(f"{bucket} - provider {provider}:\n")
                for ext, count in data.items():
                    f.write(f"  {ext}: {count} files\n")

        with open(extension_file, "w", encoding="utf-8") as f:
            f.write("Count of found extensions:\n\n")
            f.write(">> Desired extensions:\n")
            for ext in sorted(desired_extensions):
                f.write(f"{ext}: {all_extensions_count.get(ext, 0)}\n")

            f.write("\n>> Other found extensions:\n")
            for ext, count in sorted(all_extensions_count.items()):
                if ext not in desired_extensions:
                    f.write(f"{ext}: {count}\n")

        print(f"[✓] Folder '{public_content_path}' analyzed.")
        print(f"   ↳ {summary_file}")
        print(f"   ↳ {bucket_file}")
        print(f"   ↳ {extension_file}")

    print("✅ Bucket content analysis completed.")


# Command-line execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Analyze public file contents in cloud buckets")
    parser.add_argument("--config", required=True, help="Path to config.json file")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Config file not found: {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    analyze_bucket_content(config)
