import os
import shutil
import requests
from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidArgumentException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Função para pegar o tamanho do arquivo via requisição HTTP
def get_file_size(url):
    try:
        response = requests.head(url)
        if 'Content-Length' in response.headers:
            return int(response.headers['Content-Length'])
        else:
            return None  # Se o tamanho do arquivo não for encontrado
    except requests.RequestException:
        return None  # Caso ocorra algum erro na requisição

# -------------- VERIFICAR ------------- #
import config_LSTM_GPT as config
arqConfig = os.path.join('config_LSTM_GPT.py')
pasta_servidor = os.path.join('Catalogados')
#pasta_drive = os.path.join('H:/Meu Drive/Mestrado Milton')
# -------------------------------------- #

def sair(sair=False):
    if sair:
        exit(2024)
    exit(0) if input('Sair? Enter para Sair/Qualquer coisa para continuar:') == '' else None

i = 0
comeco = -1
INTERFACE_GRAFICA = False

try:
    pasta_publicos = 'ConteudoPublico'
    pasta_privados = 'ConteudoPrivado'
    fases = [f'V_{x}' for x in range(config.ultima_fase, 11)]

    for num, fase in enumerate(fases, start=config.ultima_fase):
        i = 0
        comeco = config.ultimo_bucket if comeco == -1 else 0
        pasta_saida_publicos = f'{pasta_servidor}/{fase}/{pasta_publicos}'
        os.mkdir(pasta_saida_publicos) if not os.path.isdir(pasta_saida_publicos) else None
        pasta_saida_privados = f'{pasta_servidor}/{fase}/{pasta_privados}'
        os.mkdir(pasta_saida_privados) if not os.path.isdir(pasta_saida_privados) else None

        entrada = open(f'{pasta_servidor}/{fase}/buckets_Publicos.txt', 'r', encoding='UTF-8')

        # Configurando as opções do Chrome para executar em modo headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        # Inicializa o driver do Chrome, definindo se irá ter interface gráfica
        driver = webdriver.Chrome(options=None if INTERFACE_GRAFICA else chrome_options)

        if i < comeco:
            while i < comeco:
                i += 1
                l = entrada.readline().strip()
                bucket, urlOriginal = l.split('--> ')
                print(f'{i} - {bucket}')
            sair()

        l = entrada.readline().strip()
        i += 1
        while l:
            try:
                bucket, urlOriginal = l.split('--> ')
                print(f'\n{i} - {bucket} - {urlOriginal}')
                driver.get(urlOriginal)

                elements = driver.find_elements(by=By.CLASS_NAME, value='folder')
                complementos = []
                for element in elements:
                    if int(element.get_attribute('id').removeprefix('folder')) % 2 == 1:
                        complementos.append(element.find_elements(by=By.TAG_NAME, value='span')[3].text)

                with open(f'{pasta_saida_publicos}/{bucket}.txt', 'w', encoding='UTF-8') as arqS:
                    def printArquivo(arq=arqS):
                        arq.write(urlOriginal + '\n')

                        arq.write(f'Publicos - {len(publicos)}\n')
                        for b in publicos:
                            file_size = get_file_size(b)  # Pega o tamanho do arquivo público
                            arq.write(f'--> {b} - Tamanho: {file_size} bytes\n' if file_size else f'--> {b} - Tamanho desconhecido\n')

                        arq.write(f'Nao Achados - {len(naoAchados)}\n')
                        for b in naoAchados:
                            arq.write(f'--> {b}\n')

                        arq.write(f'Outros - {len(outros)}\n')
                        for b in outros:
                            arq.write(f'--> {b}\n')

                        arq.write(f'Privados - {len(privados)}\n')
                        for b in privados:
                            arq.write(f'--> {b}\n')

                    privados = list()
                    publicos = list()
                    naoAchados = list()
                    outros = list()
                    tam = len(complementos)
                    print(f'Tamanho = {tam}\n')

                    for x, complemento in enumerate(complementos, start=1):
                        # URL da requisição
                        url = urlOriginal + ('' if str(urlOriginal).endswith('/') else '/') + complemento
                        # Realiza a requisição HEAD
                        status_code = requests.head(url).status_code

                        # Verifica se a requisição foi bem sucedida
                        if status_code == 200:
                            publicos.append(url)
                            print(f'F: {num} - P:{x}/{tam} -> {status_code} - {url}')
                        elif status_code == 403:
                            privados.append(url)
                            print(f'F: {num} - P:{x}/{tam} -> {status_code} - {url}')
                        elif status_code == 404:
                            naoAchados.append(url)
                            print(f'F: {num} - P:{x}/{tam} -> {status_code} - {url}')
                        else:
                            outros.append(f'{status_code} - {url}')
                            print(f'F: {num} - P:{x}/{tam} -> {status_code} - {url}')

                    printArquivo()

                if len(publicos) == 0:
                    shutil.move(f'{pasta_saida_publicos}/{bucket}.txt', f'{pasta_saida_privados}/{bucket}.txt')
                    print('Movido para pasta de privados!')

                l = entrada.readline().strip()
                i += 1

            except NoSuchElementException as e:
                with open(f'{pasta_saida_privados if len(publicos) != 0 else pasta_saida_publicos}/{bucket}_Exception.txt', 'w', encoding='UTF-8') as arq:
                    arq.write(f'NoSuchElementException - Analisados {len(publicos) + len(privados) + len(naoAchados) + len(outros)} de {tam}\n')
                    printArquivo(arq)
                    arq.write('\n\n')
                    arq.write(f'{url}\n')
                    arq.write(f'Mensagem: {e}')

                l = entrada.readline().strip()
                i += 1
                bucket, urlOriginal = l.split('--> ')
                print('NoSuchElementException')

            except InvalidArgumentException as e:
                with open(f'{pasta_saida_privados if len(publicos) != 0 else pasta_saida_publicos}/{bucket}_Exception.txt', 'w', encoding='UTF-8') as arq:
                    arq.write(f'InvalidArgumentException - Analisados {len(publicos) + len(privados) + len(naoAchados) + len(outros)} de {tam}\n')
                    printArquivo(arq)
                    arq.write('\n\n')
                    arq.write(f'{url}\n')
                    arq.write(f'Mensagem: {e}')

                l = entrada.readline().strip()
                i += 1
                bucket, urlOriginal = l.split('--> ')
                print('InvalidArgumentException')

            except WebDriverException as e:
                with open(f'{pasta_saida_privados if len(publicos) != 0 else pasta_saida_publicos}/{bucket}_Exception.txt', 'w', encoding='UTF-8') as arq:
                    arq.write(f'WebDriverException - Analisados {len(publicos) + len(privados) + len(naoAchados) + len(outros)} de {tam}\n')
                    printArquivo(arq)
                    arq.write('\n\n')
                    arq.write(f'{url}\n')
                    arq.write(f'Mensagem: {e}')

                l = entrada.readline().strip()
                i += 1
                bucket, urlOriginal = l.split('--> ')
                print('WebDriverException')

            except Exception as e:
                with open(f'{pasta_saida_privados if len(publicos) != 0 else pasta_saida_publicos}/{bucket}_Exception.txt', 'w', encoding='UTF-8') as arq:
                    arq.write(f'Exception  - Analisados {len(publicos) + len(privados) + len(naoAchados) + len(outros)} de {tam}\n')
                    printArquivo(arq)
                    arq.write('\n\n')
                    arq.write(f'{url}\n')
                    arq.write(f'Mensagem: {e}')

                l = entrada.readline().strip()
                i += 1
                print('Exception')
                l_split = l.split('--> ')
                if len(l_split) == 2:
                    bucket, urlOriginal = l_split
                else:
                    shutil.copytree(src=f'{pasta_saida_publicos}', dst=f'{pasta_drive}/{pasta_saida_publicos}')
                    shutil.copytree(src=f'{pasta_saida_privados}', dst=f'{pasta_drive}/{pasta_saida_privados}')
                    exit(123)

            except KeyboardInterrupt:
                with open(f'{pasta_saida_privados if len(publicos) == 0 else pasta_saida_publicos}/{bucket}_InterrompidoManual.txt', 'w', encoding='UTF-8') as arq:
                    arq.write(f'KeyBoardInterrupt - Analisados {len(publicos) + len(privados) + len(naoAchados) + len(outros)} de {tam}\n')
                    printArquivo(arq)
                with open(arqConfig, mode='w', encoding='UTF-8') as arq:
                    arq.write(f'ultimo_bucket = {i-1}\n')
                    arq.write(f'ultima_fase = {num}\n')

                exit(0)

        # Fecha o base_de_dados
        entrada.close()
        #shutil.copytree(src=f'{pasta_saida_publicos}', dst=f'{pasta_drive}/{pasta_saida_publicos}')
        #shutil.copytree(src=f'{pasta_saida_privados}', dst=f'{pasta_drive}/{pasta_saida_privados}')
        
except KeyboardInterrupt:
    with open(arqConfig, mode='w', encoding='UTF-8') as arq:
        arq.write(f'ultimo_bucket = {i - 1}\n')
        arq.write(f'ultima_fase = {num}\n')
    exit(0)
