import os
import sys
import json
import numpy as np
from numpy.random import randint
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Dense, LSTM, Embedding

from VariaveisIA import VarIA
from Letras import iniciais

# === Verifica se o dataset foi passado como argumento ===
if len(sys.argv) < 2:
    print("❌ Caminho do dataset não informado.")
    sys.exit(1)

dataset_path = sys.argv[1]

if not os.path.exists(dataset_path):
    print(f"❌ Arquivo '{dataset_path}' não encontrado.")
    sys.exit(1)

# === Caminhos auxiliares ===
script_dir = os.path.dirname(__file__)
prompt_base_dir = os.path.join(script_dir, "Prompt")
config_path = os.path.join(script_dir, "config.json")

# === Carrega configurações do arquivo JSON ===
if not os.path.exists(config_path):
    print("❌ Arquivo 'config.json' não encontrado.")
    sys.exit(1)

with open(config_path, "r", encoding="utf-8") as f:
    config_json = json.load(f)

# === Carrega dados do dataset ===
baseDeTreinamento = []
with open(dataset_path, mode='r', encoding='UTF-8') as arqTrei:
    for linha in arqTrei:
        baseDeTreinamento.append(linha.strip())

# === Pré-processamento ===
ultimoTreinamento = 0
tokenizer = Tokenizer(char_level=True)
tokenizer.fit_on_texts(baseDeTreinamento)
sequencias = tokenizer.texts_to_sequences(baseDeTreinamento)
tamanho_maximo_sequencia = max([len(seq) for seq in sequencias])
modelo = Sequential()

def treinamento(Variables: VarIA):
    global ultimoTreinamento
    unidades, epocas, taxaAprendizagem, tamanhoDeConjuntoTeste, AleatoridadeDaDivisao = Variables.get()

    sequencias_uniformes = pad_sequences(sequencias, maxlen=tamanho_maximo_sequencia, padding='post')
    X = sequencias_uniformes[:, :-1]
    y = sequencias_uniformes[:, 1:]

    X_treinamento, X_teste, y_treinamento, y_teste = train_test_split(
        X, y, test_size=tamanhoDeConjuntoTeste, random_state=AleatoridadeDaDivisao)

    modelo.add(Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=64))
    modelo.add(LSTM(units=unidades, return_sequences=True))
    modelo.add(Dense(len(tokenizer.word_index) + 1, activation='softmax'))
    modelo.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=taxaAprendizagem), metrics=['accuracy'])

    modelo.fit(X_treinamento, y_treinamento, epochs=epocas, validation_data=(X_teste, y_teste))
    ultimoTreinamento += 1

    # Cria o diretório ModelosIA se não existir
    modelo_dir = os.path.join(script_dir, "ModelosIA")
    if not os.path.exists(modelo_dir):
        os.makedirs(modelo_dir)

    modelo_path = os.path.join(modelo_dir, f"modelo_IA_{Variables.getName(ultimoTreinamento)}.keras")
    modelo.save(modelo_path)

def gerar_nome(Variaveis, caracter_inicial, tamanhoLimite=60):
    modelo_path = os.path.join(script_dir, "ModelosIA", f"modelo_IA_{Variaveis.getName(ultimoTreinamento)}.keras")
    modelo = load_model(modelo_path)
    palavra_saida = caracter_inicial

    while len(palavra_saida) < tamanhoLimite:
        sequencia = tokenizer.texts_to_sequences([palavra_saida])[0]
        sequencia_uniforme = pad_sequences([sequencia], maxlen=tamanho_maximo_sequencia - 1, padding='post')
        predicao = modelo.predict(sequencia_uniforme, verbose=0)

        try:
            proximo_indice = np.argmax(predicao[0, len(palavra_saida) - 1, :])
        except IndexError:
            print(f"{palavra_saida} - Erro de índice durante predição.")
            return palavra_saida

        next_char = tokenizer.index_word.get(proximo_indice, '')
        palavra_saida += next_char
        if next_char == '':
            break

    return palavra_saida

# === Execução principal ===
if __name__ == '__main__':
    VariaveisIA = VarIA()
    VariaveisIA.set(
        config_json["unidades"],
        config_json["epocas"],
        config_json["taxa_aprendizagem"],
        config_json["tamanho_conjunto_teste"],
        config_json["aleatoriedade_divisao"]
    )

    if input('Deseja Treinar? (s/N)? ').lower() == 's':
        treinamento(VariaveisIA)

    novosBuckets = 0
    fase = 1
    conjuntoSemRepeticao = set(sorted(baseDeTreinamento))

    if os.path.exists(prompt_base_dir):
        for arquivo in os.listdir(prompt_base_dir):
            caminho_completo = os.path.join(prompt_base_dir, arquivo)
            if os.path.isdir(caminho_completo):
                novosBuckets = 0
                try:
                    with open(os.path.join(caminho_completo, f'Saida{arquivo.split("_")[1]}_Filtrado.txt'), 'r', encoding='utf-8') as arqE:
                        for line in arqE:
                            conjuntoSemRepeticao.add(line.strip())
                            novosBuckets += 1
                    if novosBuckets >= 10000:
                        fase += 1
                except Exception:
                    pass

    tamanho_ConjuntoSemRepeticao = len(conjuntoSemRepeticao)
    pos = randint(0, len(iniciais))

    while fase <= 10:
        pasta_destino = os.path.join(prompt_base_dir, f'V_{fase}')
        if not os.path.isdir(pasta_destino):
            os.makedirs(pasta_destino)

        arq_s1 = os.path.join(pasta_destino, f'Saida{fase}.txt')
        arq_s2 = os.path.join(pasta_destino, f'Saida{fase}_Filtrado.txt')
        modo = 'a'
        precisaReTreinar = 0

        with open(arq_s1, mode=modo, encoding='utf-8') as arq, open(arq_s2, mode=modo, encoding='utf-8') as arq2:
            while novosBuckets < 10000:
                caracter_inicial = iniciais[pos]
                pos = randint(0, len(iniciais))
                precisaReTreinar += 1

                if precisaReTreinar > len(iniciais):
                    treinamento(VariaveisIA)
                    precisaReTreinar = 0

                nome_gerado = gerar_nome(VariaveisIA, caracter_inicial, tamanhoLimite=60)
                arq.write(nome_gerado + '\n')

                if nome_gerado == caracter_inicial:
                    print(f'Não gerou nada novo! {nome_gerado}')
                else:
                    conjuntoSemRepeticao.add(nome_gerado)
                    if len(conjuntoSemRepeticao) > tamanho_ConjuntoSemRepeticao:
                        print(f"{novosBuckets} --> {nome_gerado}")
                        arq2.write(nome_gerado + '\n')
                        tamanho_ConjuntoSemRepeticao += 1
                        novosBuckets += 1
                    else:
                        print(f'Repetido! - {nome_gerado}')

        novosBuckets = 0
        fase += 1
