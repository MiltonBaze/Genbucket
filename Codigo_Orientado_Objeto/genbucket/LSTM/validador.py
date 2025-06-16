import os
import requests
from GenBucket.LSTM import SeparadorFuncoes as sep  # Ajuste o import conforme o caminho real

class ValidadorBucketsLSTM:
    def __init__(self, versao=1):
        self.versao = versao
        self.pasta_versao = f'V_{self.versao}'
        self.pasta_catalogados = os.path.join('LSTM', 'Catalogados')
        self.diretorio_saida = os.path.join(self.pasta_catalogados, self.pasta_versao)

        # Criar pastas se não existirem
        os.makedirs(self.diretorio_saida, exist_ok=True)

        self.arquivo_entrada = os.path.join('LSTM', 'Prompt', self.pasta_versao, f'Saida{self.versao}_Filtrado.txt')

        # Endpoints para verificar buckets
        self.endPointList = [
            '.s3.amazonaws.com',
            '.storage.googleapis.com',
            '.fra1.digitaloceanspaces.com',
            '.nyc3.digitaloceanspaces.com',
            '.sgp1.digitaloceanspaces.com',
            '.ams3.digitaloceanspaces.com'
        ]

        sep.modoSaida = 'a'
        sep.diretorioSaida = f'./{self.diretorio_saida}/'

    def validar(self, comeco=''):
        # Abre o arquivo de entrada
        with open(self.arquivo_entrada, 'r', encoding='utf-8') as entrada:
            sep.init()

            i = 0
            bucket = entrada.readline().strip()

            # Se tiver bucket para começar a partir, pula até encontrá-lo
            if comeco != '':
                while bucket != comeco:
                    i += 1
                    print(i, bucket, sep=' - ')
                    bucket = entrada.readline().strip()

                continuar = input('Continuar? s/n: ')
                if continuar.lower() == 'n':
                    return

            while bucket:
                try:
                    i += 1
                    for endPoint in self.endPointList:
                        url = 'https://' + bucket + endPoint
                        status = requests.head(url).status_code

                        if status == 200:
                            sep.publico(bucket, url)
                            print(bucket, status, url, sep=' - ')
                        elif status == 403:
                            sep.privado(bucket, url)
                            print(bucket, status, url, sep=' - ')
                        elif status == 404:
                            sep.notFound(bucket, url)
                            print(bucket, status, url, sep=' - ')
                        elif status == 400:
                            sep.outros(bucket, url, 'Nome de bucket inválido')
                            print(bucket, 'InvalidBucketName', url, sep=' - ')
                        else:
                            sep.outros(bucket, url, status)
                    
                    print(i, bucket, sep=' - ')
                    bucket = entrada.readline().strip()

                except Exception as e:
                    sep.outros(bucket, url, f'Exception lançada! Mensagem: {e}')
                    print('Exception:', e)
                    bucket = entrada.readline().strip()
                except KeyboardInterrupt:
                    sep.newsBuckets()
                    sep.arqClose()
                    entrada.close()
                    print('Interrompido pelo usuário')
                    return

            sep.newsBuckets()
            sep.arqClose()
            print('Validação concluída')
