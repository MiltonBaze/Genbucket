import os
import json
import numpy as np
from numpy.random import randint
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Dense, LSTM, Embedding

from modelos.base import Modelo
from GenBucket.LSTM.VariaveisIA import VarIA
from GenBucket.LSTM.Letras import iniciais

class LSTMModel(Modelo):
    def __init__(self, dataset_path, config_path):
        super().__init__(dataset_path)
        self.config_path = config_path
        self.modelo = None
        self.tokenizer = Tokenizer(char_level=True)
        self.base_treinamento = []
        self.max_seq_len = 0
        self.modelo_path = ""
        self.prompt_dir = ""
        self.variaveisIA = VarIA()

    def _carregar_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            config_json = json.load(f)

        self.variaveisIA.set(
            config_json["unidades"],
            config_json["epocas"],
            config_json["taxa_aprendizagem"],
            config_json["tamanho_conjunto_teste"],
            config_json["aleatoriedade_divisao"]
        )

    def _preparar_dados(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"❌ Dataset '{self.dataset_path}' não encontrado.")

        with open(self.dataset_path, mode='r', encoding='UTF-8') as f:
            self.base_treinamento = [linha.strip() for linha in f]

        self.tokenizer.fit_on_texts(self.base_treinamento)
        sequencias = self.tokenizer.texts_to_sequences(self.base_treinamento)
        self.max_seq_len = max(len(seq) for seq in sequencias)
        return sequencias

    def _construir_modelo(self, variaveis, X_treino, y_treino, X_val, y_val):
        modelo = Sequential()
        modelo.add(Embedding(input_dim=len(self.tokenizer.word_index) + 1, output_dim=64))
        modelo.add(LSTM(units=variaveis[0], return_sequences=True))
        modelo.add(Dense(len(self.tokenizer.word_index) + 1, activation='softmax'))
        modelo.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=variaveis[2]), metrics=['accuracy'])

        modelo.fit(X_treino, y_treino, epochs=variaveis[1], validation_data=(X_val, y_val))
        return modelo

    def treinar(self):
        print("📚 Iniciando treinamento do modelo LSTM...")
        self._carregar_config()
        sequencias = self._preparar_dados()
        variaveis = self.variaveisIA.get()

        sequencias_uniformes = pad_sequences(sequencias, maxlen=self.max_seq_len, padding='post')
        X = sequencias_uniformes[:, :-1]
        y = sequencias_uniformes[:, 1:]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=variaveis[3], random_state=variaveis[4])
        self.modelo = self._construir_modelo(variaveis, X_train, y_train, X_test, y_test)

        modelo_dir = os.path.join(os.path.dirname(__file__), "..", "LSTM", "ModelosIA")
        os.makedirs(modelo_dir, exist_ok=True)
        self.modelo_path = os.path.join(modelo_dir, "modelo_lstm.keras")
        self.modelo.save(self.modelo_path)
        print(f"✅ Modelo salvo em: {self.modelo_path}")

    def _carregar_ou_treinar_modelo(self):
        self.modelo_path = os.path.join(os.path.dirname(__file__), "..", "LSTM", "ModelosIA", "modelo_lstm.keras")
        if os.path.exists(self.modelo_path):
            print(f"✅ Carregando modelo salvo: {self.modelo_path}")
            self.modelo = load_model(self.modelo_path)
        else:
            print("❌ Modelo não encontrado. Iniciando treinamento...")
            self.treinar()

    def _gerar_nome(self, letra_inicial, tamanho_maximo=60):
        saida = letra_inicial
        while len(saida) < tamanho_maximo:
            seq = self.tokenizer.texts_to_sequences([saida])[0]
            pad = pad_sequences([seq], maxlen=self.max_seq_len - 1, padding='post')
            pred = self.modelo.predict(pad, verbose=0)

            try:
                idx = np.argmax(pred[0, len(saida) - 1, :])
            except IndexError:
                break

            char = self.tokenizer.index_word.get(idx, '')
            if char == '':
                break
            saida += char

        return saida

    def gerar(self):
        print("🧠 Gerando buckets com LSTM...")
        self._carregar_config()
        self._preparar_dados()
        self._carregar_ou_treinar_modelo()

        prompt_dir = os.path.join(os.path.dirname(__file__), "..", "LSTM", "Prompt")
        os.makedirs(prompt_dir, exist_ok=True)

        conjunto = set(self.base_treinamento)
        fase = 1
        pos = randint(0, len(iniciais))

        while fase <= 10:
            destino = os.path.join(prompt_dir, f"V_{fase}")
            os.makedirs(destino, exist_ok=True)

            saida_txt = os.path.join(destino, f"Saida{fase}.txt")
            filtrado_txt = os.path.join(destino, f"Saida{fase}_Filtrado.txt")

            with open(saida_txt, "a", encoding="utf-8") as out, open(filtrado_txt, "a", encoding="utf-8") as fil:
                gerados = 0
                repetidos = 0
                while gerados < 10000:
                    letra = iniciais[pos]
                    pos = randint(0, len(iniciais))
                    nome = self._gerar_nome(letra)

                    out.write(nome + "\n")
                    if nome != letra and nome not in conjunto:
                        conjunto.add(nome)
                        fil.write(nome + "\n")
                        print(f"{gerados} --> {nome}")
                        gerados += 1
                    else:
                        repetidos += 1

                    if repetidos > len(iniciais):
                        print("⚠️ Muitos repetidos. Re-treinando...")
                        self.treinar()
                        repetidos = 0
            fase += 1

    def validar(self):
        print("🔍 Validação ainda não implementada para LSTM.")
        # TODO: Implementar como nos outros modelos

    def analisar(self):
        print("📂 Análise pública ainda não implementada para LSTM.")
        # TODO: Implementar como nos outros modelos

    def analisar_vulnerabilidades(self):
        print("🛡️ Análise de vulnerabilidades ainda não implementada para LSTM.")
        # TODO: Implementar como nos outros modelos
