import os
import re
import json
import argparse
from datetime import datetime
from modules.tools_api import ToolsAPI


def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_buckets_txt(file_path):
    buckets = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^(.*?) - provedor (\w+):$', line)
            if match:
                bucket_url = match.group(1).strip()
                provider = match.group(2).strip()
                buckets.append((bucket_url, provider))
    return buckets


def run_scans(api_tools, bucket_url):
    url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
    print(f"\n Scanning: {url}")
    result = f" Bucket: {bucket_url}\n"

    try:
        print(" ▶ Nessus...")
        api_tools.run_nessus(url)
        result += f"  ✅ Nessus: OK\n"
    except Exception as e:
        result += f"  ❌ Nessus failed: {e}\n"

    try:
        print(" ▶ Qualys WAS...")
        api_tools.run_qualys(url)
        result += f"  ✅ Qualys: OK\n"
    except Exception as e:
        result += f"  ❌ Qualys failed: {e}\n"

    return result


def analyze_vulnerabilities_2(config):
    model = config.get("model", "model")
    catalog_dir = config.get("catalogados_dir")
    report_dir = os.path.join("result", model, "vulnerability_reports(Qualys_Nessus)")
    os.makedirs(report_dir, exist_ok=True)

    api_tools = ToolsAPI(config)
    final_report = []

    for version in sorted(os.listdir(catalog_dir)):
        if version.lower().startswith("v_"):
            result_path = os.path.join(
                catalog_dir,
                version,
                f"AnalysisResult_V{version[2:]}",
                "buckets.txt"
            )

            if os.path.exists(result_path):
                print(f"\n Processing: {result_path}")
                buckets = read_buckets_txt(result_path)

                for bucket_url, _ in buckets:
                    summary = run_scans(api_tools, bucket_url)
                    final_report.append(summary)
            else:
                print(f" File not found: {result_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(report_dir, f"Vulnerability_Report_{timestamp}.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in final_report:
            f.write(line + "\n")
    print(f"\n✅ Final report saved at: {output_path}")


# Terminal execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Vulnerability scan using Nessus and Qualys")
    parser.add_argument("--config", required=True, help="Path to the model's config.json")
    args = parser.parse_args()

    config = load_config(args.config)
    analyze_vulnerabilities_2(config)
