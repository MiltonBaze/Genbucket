import os

import requests

import SeparadorFuncoes as sep

sep.modoSaida = 'a'
versao = 1
pasta_versao = f'V_{versao}'
pasta_catalogados = os.path.join('TRANSFORMER/Catalogados')
os.mkdir(f'{pasta_catalogados}') if not os.path.isdir(f'{pasta_catalogados}') else None
os.mkdir(f'{pasta_catalogados}/{pasta_versao}') if not os.path.isdir(f'{pasta_catalogados}/{pasta_versao}') else None
sep.diretorioSaida = f'./{pasta_catalogados}/{pasta_versao}/'

#entrada = open(config.saida_Filtro, 'r', encoding='UTF-8')
entrada = open(f'TRANSFORMER/Prompt/{pasta_versao}/Saida{versao}_Filtrado.txt', 'r', encoding='UTF-8')
sep.init()

endPointList = [
    '.s3.amazonaws.com',
    '.storage.googleapis.com',
    '.fra1.digitaloceanspaces.com',
    '.nyc3.digitaloceanspaces.com',
     '.sgp1.digitaloceanspaces.com',
    '.ams3.digitaloceanspaces.com'
]
i = 0
bucket = entrada.readline().strip()
comeco = ''
if comeco != '':
    while bucket != comeco:
        i += 1
        print(i,bucket, sep=' - ')
        bucket = entrada.readline().strip()

    lixo = input('Continuar?s/n')
    if lixo == 'n':
        exit(0)

while bucket:
    try:
        i += 1
        for endPoint in endPointList:
            # Navega até a URL desejada
            url = 'https://' + bucket + endPoint
            status = requests.head(url).status_code

            if status == 200: # Publico
                sep.publico(bucket, url)
                print(bucket,status,url, sep=' - ')
            elif status == 403: # Privado
                sep.privado(bucket, url)
                print(bucket,status,url, sep=' - ')
            elif status == 404: # Not Found
                sep.notFound(bucket, url)
                print(bucket,status,url, sep=' - ')
            elif status == 400:
                sep.outros(bucket, url, 'Nome de bucket inválido')
                print(bucket, 'InvalidBucketName', url, sep=' - ')
            else:
                sep.outros(bucket, url, status)

        print(i,bucket, sep=' - ')

        bucket = entrada.readline().strip()

    except Exception as e2:
        sep.outros(bucket, url, 'Exception lançado!\n\tMensagem: ' + str(e2))
        bucket = entrada.readline().strip()
        print('Exception')
        #exit(1)
    except KeyboardInterrupt:
        sep.newsBuckets()
        sep.arqClose()
        entrada.close()
        exit(0)
sep.newsBuckets()

sep.arqClose()
# Fecha o base_de_dados
entrada.close()


