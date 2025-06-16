from abc import ABC, abstractmethod

class Modelo(ABC):
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    @abstractmethod
    def treinar(self):
        pass

    @abstractmethod
    def gerar(self):
        pass

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def analisar(self):
        pass
