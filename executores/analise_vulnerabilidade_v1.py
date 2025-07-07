import os
import re
import json
import argparse
from datetime import datetime
from urllib.parse import urlparse
from ferramentas.ferramentas_vuln import executar_wapiti, executar_nuclei

def carregar_config(caminho_config):
    if not os.path.exists(caminho_config):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {caminho_config}")
    with open(caminho_config, 'r', encoding='utf-8') as f:
        return json.load(f)

def ler_buckets_txt(caminho_arquivo):
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

def rodar_analises(bucket_url, relatorio_dir):
    url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
    print(f"\n🔍 Analisando: {url}")
    resultado = f"Bucket: {bucket_url}\n"

    try:
        nome_bucket = re.sub(r'[^a-zA-Z0-9]', '_', bucket_url)
        saida_html = os.path.join(relatorio_dir, f"{nome_bucket}_wapiti.html")

        print(" ▶ Executando Wapiti...")
        executar_wapiti(url, saida_html)
        resultado += f"  ✅ Wapiti: {saida_html}\n"
    except Exception as e:
        resultado += f"  ❌ Wapiti falhou: {e}\n"

    try:
        print(" ▶ Executando Nuclei...")
        executar_nuclei(url, relatorio_dir)
        resultado += f"  ✅ Nuclei: executado com sucesso\n"
    except Exception as e:
        resultado += f"  ❌ Nuclei falhou: {e}\n"

    return resultado

def analisar_vulnerabilidades(config):
    modelo = config["modelo"]
    catalogado_dir = config.get("catalogados_dir")
    relatorio_dir = os.path.join("resultados", modelo, "relatorios")
    os.makedirs(relatorio_dir, exist_ok=True)

    relatorio_final = []

    for versao in sorted(os.listdir(catalogado_dir)):
        if versao.lower().startswith("v_"):
            resultado_path = os.path.join(
                catalogado_dir,
                versao,
                f"Resultado_AnaliseV{versao[2:]}",
                "buckets.txt"
            )

            if os.path.exists(resultado_path):
                print(f"\n📁 Processando: {resultado_path}")
                buckets = ler_buckets_txt(resultado_path)

                for bucket_url, provedor in buckets:
                    resumo = rodar_analises(bucket_url, relatorio_dir)
                    relatorio_final.append(resumo)
            else:
                print(f"⚠️ Arquivo não encontrado: {resultado_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = os.path.join(relatorio_dir, f"Relatorio_Vulnerabilidades_{timestamp}.txt")
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        for linha in relatorio_final:
            f.write(linha + "\n")
    print(f"\n✅ Relatório final salvo em: {caminho_saida}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Caminho para o arquivo config.json do modelo")
    args = parser.parse_args()

    config = carregar_config(args.config)
    analisar_vulnerabilidades(config)

if __name__ == "__main__":
    main()
