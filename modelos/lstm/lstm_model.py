from modelos.base_model import BaseModel
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import numpy as np
import os
import pickle

class LSTMModel(BaseModel):
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.tokenizer = None

        
        self.output_dir = config.get("modelo_treinado_dir", "resultados/lstm/modelos_treinados")
        self.tokenizer_path = os.path.join(self.output_dir, "tokenizer.pkl")
        os.makedirs(self.output_dir, exist_ok=True)

    def fit(self, dataset_path: str):
        print(" Iniciando treinamento do modelo LSTM...")

        # Lê os hiperparâmetros do config
        unidades = self.config.get("lstm_units", self.config.get("unidades", 64))
        epocas = self.config.get("epochs", self.config.get("epocas", 200))
        taxa_aprendizado = self.config.get("learning_rate", self.config.get("taxa_aprendizagem", 0.001))
        tamanho_teste = self.config.get("test_size", self.config.get("tamanho_conjunto_teste", 0.2))
        random_state = self.config.get("random_state", self.config.get("aleatoriedade_divisao", 42))
        max_len = self.config.get("max_len", self.config.get("maxlen", 20))

        with open(dataset_path, "r", encoding="utf-8") as f:
            texto = f.read().lower()

        from tensorflow.keras.preprocessing.text import Tokenizer
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts([texto])

        words = texto.split()
        sequences = []
        for i in range(1, len(words)):
            seq = words[:i + 1]
            encoded = self.tokenizer.texts_to_sequences([' '.join(seq)])[0]
            if len(encoded) > 1:
                sequences.append(encoded)

        max_len_dataset = max([len(seq) for seq in sequences])
        sequences = pad_sequences(sequences, maxlen=max_len_dataset, padding='pre')
        X = sequences[:, :-1]
        y = sequences[:, -1]
        y = np.expand_dims(y, -1)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=tamanho_teste, random_state=random_state
        )

        vocab_size = len(self.tokenizer.word_index) + 1

        self.model = Sequential()
        self.model.add(Embedding(input_dim=vocab_size, output_dim=64, input_length=X.shape[1]))
        self.model.add(LSTM(units=unidades))
        self.model.add(Dense(vocab_size, activation='softmax'))

        self.model.compile(loss='sparse_categorical_crossentropy',
                           optimizer=Adam(learning_rate=taxa_aprendizado),
                           metrics=['accuracy'])

        self.model.fit(X_train, y_train, epochs=epocas, validation_data=(X_test, y_test))

        self.model.save(os.path.join(self.output_dir, "lstm_model.h5"))
        with open(self.tokenizer_path, "wb") as f:
            pickle.dump(self.tokenizer, f)

        print(f"✅ Modelo salvo em: {self.output_dir}")

    def predict(self, prompt: str, **kwargs):
        if self.model is None:
            self.model = load_model(os.path.join(self.output_dir, "lstm_model.h5"))
            with open(self.tokenizer_path, "rb") as f:
                self.tokenizer = pickle.load(f)

        num_words = kwargs.get("num_words", 20)
        max_len = self.config.get("max_len", self.config.get("maxlen", 20))
        result = prompt.lower()

        for _ in range(num_words):
            encoded = self.tokenizer.texts_to_sequences([result])[0]
            encoded = pad_sequences([encoded], maxlen=max_len, padding='pre')
            pred = self.model.predict(encoded, verbose=0)
            next_word_id = pred.argmax(axis=-1)[0]

            for word, index in self.tokenizer.word_index.items():
                if index == next_word_id:
                    result += ' ' + word
                    break

        return [result]
