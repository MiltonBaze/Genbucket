import os
import re
import json
import argparse
from datetime import datetime
from urllib.parse import urlparse
from modules.tools_vuln import run_wapiti, run_nuclei

def load_config(caminho_config):
    if not os.path.exists(caminho_config):
        print(f"❌ Arquivo de configuração não encontrado: {caminho_config}")
        exit(1)
    with open(caminho_config, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_buckets_txt(caminho_arquivo):
    buckets = []
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            match = re.match(r'^(.*?) - provedor (\w+):$', linha)
            if match:
                bucket_url = match.group(1).strip()
                provedor = match.group(2).strip()
                buckets.append((bucket_url, provedor))
    return buckets

def analyze_run(bucket_url, relatorio_dir, config):
    url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
    print(f"\n Analyzing: {url}")
    resultado = f"Bucket: {bucket_url}\n"

    wapiti_path = config.get("wapiti_path", os.path.join("tools", "wapiti"))
    nuclei_path = config.get("nuclei_path", os.path.join("tools", "nuclei"))

    try:
        nome_bucket = re.sub(r'[^a-zA-Z0-9]', '_', bucket_url)
        saida_html = os.path.join(relatorio_dir, f"{nome_bucket}_wapiti.html")
        print(" ▶ Running Wapiti...")
        run_wapiti(url, saida_html, wapiti_path)
        resultado += f"  ✅ Wapiti: {saida_html}\n"
    except Exception as e:
        resultado += f"  ❌ Wapiti falhou: {e}\n"

    try:
        print(" ▶ Run Nuclei...")
        run_nuclei(url, relatorio_dir, nuclei_path)
        resultado += f"  ✅ Nuclei: successfully executed\n"
    except Exception as e:
        resultado += f"  ❌ Nuclei failed: {e}\n"

    return resultado

def analyze_vulnerabilities_1(config):
    modelo = config.get("model", "model")
    catalogado_dir = config.get("catalogados_dir")
    relatorio_dir = os.path.join("result", modelo, "Vulnerability_reports(Nuclei_Wapiti)")
    os.makedirs(relatorio_dir, exist_ok=True)

    relatorio_final = []

    for versao in sorted(os.listdir(catalogado_dir)):
        if versao.lower().startswith("v_"):
            resultado_path = os.path.join(
                catalogado_dir,
                versao,
                f"AnalysisResult_V{versao[2:]}",
                "buckets.txt"
            )

            if os.path.exists(resultado_path):
                print(f"\n processing: {resultado_path}")
                buckets = read_buckets_txt(resultado_path)

                for bucket_url, provedor in buckets:
                    resumo = analyze_run(bucket_url, relatorio_dir, config)
                    relatorio_final.append(resumo)
            else:
                print(f" File not found: {resultado_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = os.path.join(relatorio_dir, f"vulnerability_reports_{timestamp}.txt")
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        for linha in relatorio_final:
            f.write(linha + "\n")
    print(f"\n✅ Final report saved in: {caminho_saida}")

# Execução via terminal (padrão dos outros scripts)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vulnerability Scanner for Public Buckets.")
    parser.add_argument("--config", required=True, help="Path to config.json file")
    args = parser.parse_args()

    config = carregar_config(args.config)
    analyze_vulnerabilities_1(config)
