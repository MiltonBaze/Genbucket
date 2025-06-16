# verificador_lstm.py

import os
import shutil
import requests

from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidArgumentException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class VerificadorBucketsPublicosLSTM:
    def __init__(self, config_module, pasta_servidor='LSTM/Catalogados', interface_grafica=False):
        self.config = config_module
        self.pasta_servidor = pasta_servidor
        self.interface_grafica = interface_grafica
        self.pasta_publicos = 'ConteudoPublico'
        self.pasta_privados = 'ConteudoPrivado'
        self.fases = [f'V_{x}' for x in range(self.config.ultima_fase, 11)]
        self.arq_config_path = 'config_buckets.py'

    def verificar(self):
        try:
            for num, fase in enumerate(self.fases, start=self.config.ultima_fase):
                i = 0
                comeco = self.config.ultimo_bucket if num == self.config.ultima_fase else 0

                pasta_saida_publicos = os.path.join(self.pasta_servidor, fase, self.pasta_publicos)
                pasta_saida_privados = os.path.join(self.pasta_servidor, fase, self.pasta_privados)
                os.makedirs(pasta_saida_publicos, exist_ok=True)
                os.makedirs(pasta_saida_privados, exist_ok=True)

                entrada_path = os.path.join(self.pasta_servidor, fase, 'buckets_Publicos.txt')
                with open(entrada_path, 'r', encoding='utf-8') as entrada:
                    chrome_options = Options()
                    if not self.interface_grafica:
                        chrome_options.add_argument('--headless')
                    driver = webdriver.Chrome(options=None if self.interface_grafica else chrome_options)

                    if i < comeco:
                        while i < comeco:
                            i += 1
                            bucket, _ = entrada.readline().strip().split('--> ')
                            print(f'{i} - {bucket}')
                        if input('Sair? Enter para Sair/Outro para continuar: ') == '':
                            return

                    for linha in entrada:
                        i += 1
                        bucket, urlOriginal = linha.strip().split('--> ')
                        print(f'\n{i} - {bucket} - {urlOriginal}')
                        driver.get(urlOriginal)

                        try:
                            elements = driver.find_elements(By.CLASS_NAME, 'folder')
                            complementos = [
                                el.find_elements(By.TAG_NAME, 'span')[3].text
                                for el in elements
                                if int(el.get_attribute('id').removeprefix('folder')) % 2 == 1
                            ]

                            saida_path = os.path.join(pasta_saida_publicos, f'{bucket}.txt')
                            with open(saida_path, 'w', encoding='utf-8') as arqS:
                                publicos, privados, naoAchados, outros = [], [], [], []
                                for x, complemento in enumerate(complementos, start=1):
                                    url = f'{urlOriginal.rstrip("/")}/{complemento}'
                                    status_code = requests.head(url).status_code

                                    if status_code == 200:
                                        publicos.append(url)
                                    elif status_code == 403:
                                        privados.append(url)
                                    elif status_code == 404:
                                        naoAchados.append(url)
                                    else:
                                        outros.append(f'{status_code} - {url}')

                                    print(f'F:{num} - P:{x}/{len(complementos)} -> {status_code} - {url}')

                                self._salvar_resultado(arqS, urlOriginal, publicos, privados, naoAchados, outros)

                            if not publicos:
                                shutil.move(saida_path, os.path.join(pasta_saida_privados, f'{bucket}.txt'))
                                print('Movido para pasta de privados!')

                        except Exception as e:
                            self._registrar_excecao(e, bucket, urlOriginal, pasta_saida_publicos, pasta_saida_privados, publicos, privados, naoAchados, outros, len(complementos))
                            continue

        except KeyboardInterrupt:
            with open(self.arq_config_path, 'w', encoding='utf-8') as arq:
                arq.write(f'ultimo_bucket = {i - 1}\n')
                arq.write(f'ultima_fase = {num}\n')
            print("Execução interrompida manualmente. Progresso salvo.")

    def _salvar_resultado(self, arquivo, urlOriginal, publicos, privados, naoAchados, outros):
        arquivo.write(urlOriginal + '\n')
        for label, items in [
            ('Publicos', publicos),
            ('Nao Achados', naoAchados),
            ('Outros', outros),
            ('Privados', privados)
        ]:
            arquivo.write(f'{label} - {len(items)}\n')
            for item in items:
                arquivo.write(f'--> {item}\n')

    def _registrar_excecao(self, exc, bucket, url, pasta_publicos, pasta_privados, publicos, privados, naoAchados, outros, total):
        nome_arquivo = f'{bucket}_Exception.txt'
        destino = pasta_privados if not publicos else pasta_publicos
        with open(os.path.join(destino, nome_arquivo), 'w', encoding='utf-8') as arq:
            arq.write(f'{exc.__class__.__name__} - Analisados {len(publicos) + len(privados) + len(naoAchados) + len(outros)} de {total}\n')
            self._salvar_resultado(arq, url, publicos, privados, naoAchados, outros)
            arq.write('\n\n')
            arq.write(f'{url}\n')
            arq.write(f'Mensagem: {exc}')
