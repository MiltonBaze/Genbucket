import os
import sys
import json
import time
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, WebDriverException
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verificar_buckets_publicos(config):
    catalogados_dir = config.get("catalogados_dir")
    if not catalogados_dir or not os.path.exists(catalogados_dir):
        raise FileNotFoundError(f"Pasta catalogados_dir inválida ou não existe: {catalogados_dir}")

    ultima_fase = config.get("ultima_fase", 1)
    ultimo_bucket = config.get("ultimo_bucket", 0)
    modelo_nome = config.get("modelo", "modelo")
    max_fase = 10

    pasta_publicos = "ConteudoPublico"
    pasta_privados = "ConteudoPrivado"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for fase_num in range(ultima_fase, max_fase + 1):
            fase = f"V_{fase_num}"
            print(f"\n🔍 Verificando fase {fase}...")

            pasta_fase = os.path.join(catalogados_dir, fase)
            if not os.path.exists(pasta_fase):
                print(f"❌ Pasta da fase não encontrada: {pasta_fase}. Pulando...")
                continue

            pasta_publicos_fase = os.path.join(pasta_fase, pasta_publicos)
            pasta_privados_fase = os.path.join(pasta_fase, pasta_privados)
            os.makedirs(pasta_publicos_fase, exist_ok=True)
            os.makedirs(pasta_privados_fase, exist_ok=True)

            arquivo_buckets = os.path.join(pasta_fase, "buckets_Publicos.txt")
            if not os.path.exists(arquivo_buckets):
                print(f"❌ Arquivo {arquivo_buckets} não encontrado. Pulando fase...")
                continue

            with open(arquivo_buckets, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            i = 0
            if fase_num == ultima_fase:
                i = ultimo_bucket

            for idx, linha in enumerate(linhas):
                if idx < i:
                    continue
                linha = linha.strip()
                if not linha or "--> " not in linha:
                    continue
                bucket, url_base = linha.split("--> ")
                print(f"\n{idx+1} - Verificando bucket: {bucket} - {url_base}")

                try:
                    driver.get(url_base)
                    time.sleep(1)

                    elementos = driver.find_elements(By.CLASS_NAME, "folder")
                    complementos = []
                    for el in elementos:
                        try:
                            el_id = el.get_attribute("id")
                            if el_id and el_id.startswith("folder") and int(el_id[6:]) % 2 == 1:
                                spans = el.find_elements(By.TAG_NAME, "span")
                                if len(spans) > 3:
                                    complementos.append(spans[3].text)
                        except Exception:
                            continue

                    urls_publicos, urls_privados, urls_nao_achados, urls_outros = [], [], [], []

                    for pos, comp in enumerate(complementos, start=1):
                        url_verif = url_base.rstrip("/") + "/" + comp
                        try:
                            status = requests.head(url_verif, timeout=10).status_code
                        except requests.RequestException:
                            status = 0

                        if status == 200:
                            urls_publicos.append(url_verif)
                        elif status == 403:
                            urls_privados.append(url_verif)
                        elif status == 404:
                            urls_nao_achados.append(url_verif)
                        else:
                            urls_outros.append(f"{status} - {url_verif}")

                    arquivo_saida = os.path.join(
                        pasta_publicos_fase if urls_publicos else pasta_privados_fase,
                        f"{bucket}.txt"
                    )

                    with open(arquivo_saida, "w", encoding="utf-8") as saida:
                        saida.write(url_base + "\n\n")
                        saida.write(f"Públicos ({len(urls_publicos)}):\n")
                        saida.writelines([f"--> {u}\n" for u in urls_publicos])
                        saida.write(f"\nNão Achados ({len(urls_nao_achados)}):\n")
                        saida.writelines([f"--> {u}\n" for u in urls_nao_achados])
                        saida.write(f"\nOutros ({len(urls_outros)}):\n")
                        saida.writelines([f"--> {u}\n" for u in urls_outros])
                        saida.write(f"\nPrivados ({len(urls_privados)}):\n")
                        saida.writelines([f"--> {u}\n" for u in urls_privados])

                    print(f"✅ Bucket {bucket} verificado.")

                except (NoSuchElementException, InvalidArgumentException, WebDriverException) as e:
                    print(f"❌ Erro Selenium no bucket {bucket}: {e}")
                except Exception as e:
                    print(f"❌ Erro inesperado no bucket {bucket}: {e}")

                i += 1

            config["ultima_fase"] = fase_num
            config["ultimo_bucket"] = i
            config_path_out = os.path.join("resultados", modelo_nome, "config.json")
            os.makedirs(os.path.dirname(config_path_out), exist_ok=True)
            with open(config_path_out, "w", encoding="utf-8") as cf:
                json.dump(config, cf, indent=2)

    except KeyboardInterrupt:
        print("\n⛔ Execução interrompida manualmente.")
    finally:
        driver.quit()
        print("\n Processo finalizado.")

def main():
    parser = argparse.ArgumentParser(description="🔍 Verifica buckets públicos e privados")
    parser.add_argument("--config", required=True, help="Caminho para o arquivo config.json")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Arquivo de configuração não encontrado: {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    verificar_buckets_publicos(config)

if __name__ == "__main__":
    main()
