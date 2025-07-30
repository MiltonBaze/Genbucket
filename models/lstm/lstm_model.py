import os
import json
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam
from models.base_model import BaseModel


class LSTMModel(BaseModel):
    def __init__(self, config):
        self.config = config
        self.model_dir = config.get("modelo_treinado_dir", "Result/lstm/models_training")
        self.tokenizer_path = os.path.join(self.model_dir, "tokenizer.json")
        self.model_path = os.path.join(self.model_dir, "lstm_model.keras")
        self.max_len = self.config.get("max_len", 30)
        self.tokenizer = None
        self.model = None

    def fit(self, dataset_path: str):
        with open(dataset_path, "r", encoding="utf-8") as f:
            nomes = [linha.strip().lower() for linha in f if linha.strip()]

        tokenizer = Tokenizer(char_level=True)
        tokenizer.fit_on_texts(nomes)
        self.tokenizer = tokenizer

        sequencias = tokenizer.texts_to_sequences(nomes)
        tamanho_max = max([len(seq) for seq in sequencias])
        sequencias_uniformes = pad_sequences(sequencias, maxlen=tamanho_max, padding='post')

        X = sequencias_uniformes[:, :-1]
        y = sequencias_uniformes[:, 1:]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.get("test_size", 0.2), random_state=self.config.get("random_state", 42)
        )

        vocab_size = len(tokenizer.word_index) + 1

        model = Sequential()
        model.add(Embedding(input_dim=vocab_size, output_dim=64))
        model.add(LSTM(units=self.config.get("units", 64), return_sequences=True))
        model.add(Dense(vocab_size, activation='softmax'))

        optimizer = Adam(learning_rate=self.config.get("learning_rate", 0.001))
        model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

        model.fit(X_train, y_train, epochs=self.config.get("epochs", 100), validation_data=(X_test, y_test))

        os.makedirs(self.model_dir, exist_ok=True)
        model.save(self.model_path)

        with open(self.tokenizer_path, "w", encoding="utf-8") as f:
            f.write(tokenizer.to_json())

        print(f"✅ Modelo salvo em: {self.model_path}")
        print(f"✅ Tokenizer salvo em: {self.tokenizer_path}")

    def predict(self, prompt: str, max_chars=60):
        if not self.tokenizer:
            with open(self.tokenizer_path, "r", encoding="utf-8") as f:
                self.tokenizer = tokenizer_from_json(f.read())

        if not self.model:
            self.model = load_model(self.model_path)

        palavra_saida = prompt.lower()
        index_word = {v: k for k, v in self.tokenizer.word_index.items()}

        while len(palavra_saida) < max_chars:
            seq = self.tokenizer.texts_to_sequences([palavra_saida])[0]
            seq = pad_sequences([seq], maxlen=self.max_len - 1, padding='post')

            pred = self.model.predict(seq, verbose=0)
            try:
                proximo_indice = np.argmax(pred[0, len(palavra_saida) - 1, :])
            except IndexError:
                break

            next_char = index_word.get(proximo_indice, '')
            if not next_char:
                break

            palavra_saida += next_char

        return [palavra_saida.strip()]
