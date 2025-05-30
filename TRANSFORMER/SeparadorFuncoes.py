arqPrivados = None
arqPublicos = None
arqRedirecionados = None
arqNotFound = None
arqOutros = None
arqBuckets = None
listaBucketsSemRepeticao = set()

modoSaida = None
diretorioSaida = None

def init(privado=True, publico=True, redirecionado=False,notFound=True,outros=True,bucket=True):
    global diretorioSaida, modoSaida, arqPrivados, arqPublicos, arqRedirecionados, arqNotFound, arqOutros, arqBuckets

    if privado:
        nome_arqPrivados = 'buckets_Privados.txt'
        arqPrivados = open(diretorioSaida+nome_arqPrivados, mode=modoSaida, encoding='UTF-8')
    if publico:
        nome_arqPublicos = 'buckets_Publicos.txt'
        arqPublicos = open(diretorioSaida+nome_arqPublicos, mode=modoSaida, encoding='UTF-8')
    if redirecionado:
        nome_arqRedirecionados = 'buckets_Redirecionados.txt'
        arqRedirecionados = open(diretorioSaida+nome_arqRedirecionados, mode=modoSaida, encoding='UTF-8')
    if notFound:
        nome_arqNotFound = 'buckets_NotFound.txt'
        arqNotFound = open(diretorioSaida+nome_arqNotFound, mode=modoSaida, encoding='UTF-8')
    if outros:
        nome_arqOutros = 'buckets_Outros.txt'
        arqOutros = open(diretorioSaida+nome_arqOutros, mode=modoSaida, encoding='UTF-8')
    if bucket:
        nome_arqBuckets = 'buckets_Buckets.txt'
        arqBuckets = open(diretorioSaida+nome_arqBuckets, mode=modoSaida, encoding='UTF-8')



def notFound(bucket, endereco):
    arqNotFound.write(bucket + '--> ' + endereco +'\n')

def privado(bucket, endereco):
    arqPrivados.write(bucket + '--> ' + endereco +'\n')
    listaBucketsSemRepeticao.add(bucket)

def publico(bucket, endereco):
    arqPublicos.write(bucket + '--> ' + endereco +'\n')
    listaBucketsSemRepeticao.add(bucket)

def redirecionamento(enderecoOriginal, enderecoRedirecionado):
    arqRedirecionados.write(enderecoOriginal + ' --> ' + enderecoRedirecionado+'\n')

def outros(bucket, url, mensagem):
    arqOutros.write(bucket + ' --> ' + url + '\n\tMensagem: --> ' + str(mensagem) +'\n')

def newsBuckets():
    if arqBuckets is not None:
        for bucketName in listaBucketsSemRepeticao:
            arqBuckets.write(bucketName+'\n')

def arqClose():
    if arqRedirecionados is not None:
        arqRedirecionados.close()
    if arqNotFound is not None:
        arqNotFound.close()
    if arqPrivados is not None:
        arqPrivados.close()
    if arqPublicos is not None:
        arqPublicos.close()
    if arqOutros is not None:
        arqOutros.close()
    if arqBuckets is not None:
        arqBuckets.close()