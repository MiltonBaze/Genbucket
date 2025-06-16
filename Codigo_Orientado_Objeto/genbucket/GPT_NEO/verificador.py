import os
import shutil
import requests
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    InvalidArgumentException,
    WebDriverException
)
from selenium.webdriver.common.by import By


class VerificadorBucketsPublicos:
    def __init__(self, config_path, interface_grafica=False):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Arquivo de configuração não encontrado: {config_path}")

        self.config_path = config_path
        self.interface_grafica = interface_grafica

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.pasta_base = os.path.dirname(config_path)
        self.pasta_catalogados = os.path.join(self.pasta_base, "Catalogados")
        self.fase_inicial = self.config.get("ultima_fase", 1)
        self.bucket_inicial = self.config.get("ultimo_bucket", 0)

        self.pasta_publicos = "ConteudoPublico"
        self.pasta_privados = "ConteudoPrivado"

    def _configurar_driver(self):
        chrome_options = Options()
        if not self.interface_grafica:
            chrome_options.add_argument('--headless')
        return webdriver.Chrome(options=chrome_options)

    def _get_file_size(self, url):
        try:
            response = requests.head(url)
            return int(response.headers.get("Content-Length", 0))
        except requests.RequestException:
            return None

    def verificar(self):
        fases = [f"V_{x}" for x in range(self.fase_inicial, 11)]
        driver = self._configurar_driver()
        i = 0

        try:
            for num, fase in enumerate(fases, start=self.fase_inicial):
                print(f"🔍 Verificando fase: {fase}")

                pasta_fase = os.path.join(self.pasta_catalogados, fase)
                os.makedirs(pasta_fase, exist_ok=True)
                pasta_saida_publicos = os.path.join(pasta_fase, self.pasta_publicos)
                pasta_saida_privados = os.path.join(pasta_fase, self.pasta_privados)
                os.makedirs(pasta_saida_publicos, exist_ok=True)
                os.makedirs(pasta_saida_privados, exist_ok=True)

                path_entrada = os.path.join(pasta_fase, "buckets_Publicos.txt")
                if not os.path.exists(path_entrada):
                    print(f"❌ Arquivo não encontrado: {path_entrada}")
                    continue

                with open(path_entrada, "r", encoding="utf-8") as entrada:
                    for linha in entrada:
                        i += 1
                        if i < self.bucket_inicial:
                            continue

                        if "--> " not in linha:
                            continue
                        bucket, url_original = linha.strip().split("--> ")

                        print(f"\n{i} - {bucket} - {url_original}")
                        driver.get(url_original)

                        elementos = driver.find_elements(by=By.CLASS_NAME, value="folder")
                        complementos = []
                        for el in elementos:
                            try:
                                if int(el.get_attribute("id").removeprefix("folder")) % 2 == 1:
                                    span = el.find_elements(by=By.TAG_NAME, value="span")[3].text
                                    complementos.append(span)
                            except Exception:
                                continue

                        urls_publicos, urls_privados, urls_nao_achados, urls_outros = [], [], [], []

                        for complemento in complementos:
                            url = f"{url_original.rstrip('/')}/{complemento}"
                            try:
                                status = requests.head(url).status_code
                            except requests.RequestException:
                                status = 0

                            if status == 200:
                                urls_publicos.append(url)
                            elif status == 403:
                                urls_privados.append(url)
                            elif status == 404:
                                urls_nao_achados.append(url)
                            else:
                                urls_outros.append(f"{status} - {url}")

                        # Decide onde salvar
                        if urls_publicos:
                            path_saida = os.path.join(pasta_saida_publicos, f"{bucket}.txt")
                        else:
                            path_saida = os.path.join(pasta_saida_privados, f"{bucket}.txt")

                        with open(path_saida, "w", encoding="utf-8") as saida:
                            saida.write(url_original + "\n")
                            saida.write(f"Publicos - {len(urls_publicos)}\n")
                            saida.writelines([f"--> {url}\n" for url in urls_publicos])

                            saida.write(f"Nao Achados - {len(urls_nao_achados)}\n")
                            saida.writelines([f"--> {url}\n" for url in urls_nao_achados])

                            saida.write(f"Outros - {len(urls_outros)}\n")
                            saida.writelines([f"--> {url}\n" for url in urls_outros])

                            saida.write(f"Privados - {len(urls_privados)}\n")
                            saida.writelines([f"--> {url}\n" for url in urls_privados])

                        print(f"✅ {bucket} verificado. Público: {len(urls_publicos)}")

        except KeyboardInterrupt:
            print("\n⛔ Interrompido manualmente.")
        finally:
            driver.quit()
            self._salvar_estado(i, num)
            print("📝 Estado salvo em config.json.")

    def _salvar_estado(self, ultimo_bucket, ultima_fase):
        self.config["ultimo_bucket"] = ultimo_bucket
        self.config["ultima_fase"] = ultima_fase
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
