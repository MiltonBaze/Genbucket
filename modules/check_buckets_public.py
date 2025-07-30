import os
import json
import time
import requests
import sys
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    InvalidArgumentException,
    WebDriverException,
)

def check_buckets(config):
    catalog_dir = config.get("catalogados_dir")
    if not catalog_dir or not os.path.exists(catalog_dir):
        raise FileNotFoundError(f"Invalid or non-existent catalog directory: {catalog_dir}")

    last_phase = config.get("ultima_fase", 1)
    last_bucket = config.get("ultimo_bucket", 0)
    model_name = config.get("model", "model")
    max_phase = 10

    public_folder = "PublicContent"
    private_folder = "PrivateContent"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for phase_number in range(last_phase, max_phase + 1):
            phase = f"V_{phase_number}"
            print(f"\n🔍 Checking phase {phase}...")

            phase_dir = os.path.join(catalog_dir, phase)
            if not os.path.exists(phase_dir):
                print(f"❌ Phase folder not found: {phase_dir}. Skipping...")
                continue

            public_phase_dir = os.path.join(phase_dir, public_folder)
            private_phase_dir = os.path.join(phase_dir, private_folder)
            os.makedirs(public_phase_dir, exist_ok=True)
            os.makedirs(private_phase_dir, exist_ok=True)

            buckets_file = os.path.join(phase_dir, "buckets_Publicos.txt")
            if not os.path.exists(buckets_file):
                print(f"❌ File not found: {buckets_file}. Skipping phase...")
                continue

            with open(buckets_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            i = 0
            if phase_number == last_phase:
                i = last_bucket

            for idx, line in enumerate(lines):
                if idx < i:
                    continue

                line = line.strip()
                if not line or "--> " not in line:
                    continue

                bucket, base_url = line.split("--> ")
                print(f"\n{idx+1} - Checking bucket: {bucket} - {base_url}")

                try:
                    driver.get(base_url)
                    time.sleep(1)

                    elements = driver.find_elements(By.CLASS_NAME, "folder")
                    subpaths = []

                    for el in elements:
                        try:
                            el_id = el.get_attribute("id")
                            if el_id and el_id.startswith("folder") and int(el_id[6:]) % 2 == 1:
                                spans = el.find_elements(By.TAG_NAME, "span")
                                if len(spans) > 3:
                                    subpaths.append(spans[3].text)
                        except Exception:
                            continue

                    urls_public, urls_private, urls_not_found, urls_other = [], [], [], []

                    for sub in subpaths:
                        check_url = base_url.rstrip("/") + "/" + sub
                        try:
                            status = requests.head(check_url, timeout=10).status_code
                        except requests.RequestException:
                            status = 0

                        if status == 200:
                            urls_public.append(check_url)
                        elif status == 403:
                            urls_private.append(check_url)
                        elif status == 404:
                            urls_not_found.append(check_url)
                        else:
                            urls_other.append(f"{status} - {check_url}")

                    output_file = os.path.join(
                        public_phase_dir if urls_public else private_phase_dir,
                        f"{bucket}.txt"
                    )

                    with open(output_file, "w", encoding="utf-8") as out:
                        out.write(base_url + "\n\n")
                        out.write(f"Public ({len(urls_public)}):\n")
                        out.writelines([f"--> {u}\n" for u in urls_public])
                        out.write(f"\nNot Found ({len(urls_not_found)}):\n")
                        out.writelines([f"--> {u}\n" for u in urls_not_found])
                        out.write(f"\nOther ({len(urls_other)}):\n")
                        out.writelines([f"--> {u}\n" for u in urls_other])
                        out.write(f"\nPrivate ({len(urls_private)}):\n")
                        out.writelines([f"--> {u}\n" for u in urls_private])

                    print(f"✅ Bucket {bucket} checked.")

                except (NoSuchElementException, InvalidArgumentException, WebDriverException) as e:
                    print(f"❌ Selenium error on bucket {bucket}: {e}")
                except Exception as e:
                    print(f"❌ Unexpected error on bucket {bucket}: {e}")

                i += 1

            # Save progress
            config["ultima_fase"] = phase_number
            config["ultimo_bucket"] = i
            config_path_out = os.path.join("results", model_name, "config.json")
            os.makedirs(os.path.dirname(config_path_out), exist_ok=True)
            with open(config_path_out, "w", encoding="utf-8") as cf:
                json.dump(config, cf, indent=2)

    except KeyboardInterrupt:
        print("\n⛔ Execution interrupted manually.")
    finally:
        driver.quit()
        print("\n✅ Process completed.")


# Direct execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Check public and private buckets")
    parser.add_argument("--config", required=True, help="Path to the config.json file")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Config file not found: {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    check_buckets(config)
