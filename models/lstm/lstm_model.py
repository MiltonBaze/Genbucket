import os
import json
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from models.base_model import BaseModel


class LSTMModel(BaseModel):
    def __init__(self, config):
        self.config = config
        self.model_dir = config.get("modelo_treinado_dir", "Result/lstm/models_training")
        self.tokenizer_path = os.path.join(self.model_dir, "tokenizer.json")
        self.model_path = os.path.join(self.model_dir, "lstm_model.h5")
        self.max_len = self.config.get("max_len", 30)
        self.tokenizer = None
        self.model = None

    def fit(self, dataset_path: str):
        # Etapa 1: Leitura e concatenação com separador \n
        with open(dataset_path, "r", encoding="utf-8") as f:
            nomes = [linha.strip().lower() for linha in f if linha.strip()]
        
        nomes = [n for n in nomes if 5 < len(n) <= self.max_len]
        texto_unico = "\n".join(nomes)

        # Tokenização a nível de caractere
        tokenizer = Tokenizer(char_level=True, lower=True)
        tokenizer.fit_on_texts([texto_unico])
        total_seq = tokenizer.texts_to_sequences([texto_unico])[0]

        # Criação de sequências com janela deslizante
        input_sequences = []
        for i in range(1, len(total_seq)):
            ngram = total_seq[:i + 1]
            input_sequences.append(ngram)

        input_sequences = pad_sequences(input_sequences, maxlen=self.max_len, padding='pre')
        X = input_sequences[:, :-1]
        y = input_sequences[:, -1]
        vocab_size = len(tokenizer.word_index) + 1

        model = Sequential()
        model.add(Embedding(input_dim=vocab_size, output_dim=64, input_length=X.shape[1]))
        model.add(LSTM(128))
        model.add(Dense(vocab_size, activation='softmax'))

        model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(X, y, batch_size=32, epochs=self.config.get("epochs", 20))

        os.makedirs(self.model_dir, exist_ok=True)
        model.save(self.model_path)

        with open(self.tokenizer_path, "w", encoding="utf-8") as f:
            f.write(tokenizer.to_json())

        print(f"✅ Modelo salvo em: {self.model_path}")
        print(f"✅ Tokenizer salvo em: {self.tokenizer_path}")

    def sample_with_temperature(self, preds, temperature=1.0):
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds + 1e-8) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        return np.random.choice(len(preds), p=preds)

    def predict(self, prompt: str = "", **kwargs):
        from keras.utils import pad_sequences

        max_len = self.config.get("max_len", 30)
        temperature = kwargs.get("temperature", 0.8)
        max_chars = kwargs.get("max_chars", 50)

        if not self.tokenizer:
            with open(self.tokenizer_path, "r", encoding="utf-8") as f:
                tokenizer_json = json.dumps(json.load(f))
                self.tokenizer = tokenizer_from_json(tokenizer_json)

        if not self.model:
            self.model = load_model(self.model_path)

        result = prompt.lower()
        index_word = {v: k for k, v in self.tokenizer.word_index.items()}
        word_index = self.tokenizer.word_index

        for _ in range(max_chars):
            seq = self.tokenizer.texts_to_sequences([result[-(max_len - 1):]])[0]
            seq = pad_sequences([seq], maxlen=max_len - 1, padding="pre")
            predicted = self.model.predict(seq, verbose=0)[0]
            next_index = self.sample_with_temperature(predicted, temperature)
            next_char = index_word.get(next_index)

            if not next_char:
                break
            if next_char == "\n":
                break
            result += next_char

        return [result.strip()]