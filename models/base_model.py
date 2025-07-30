from abc import ABC, abstractmethod

class BaseModel(ABC):
     
    @abstractmethod
    def fit(self, dataset_path: str):
        pass

    @abstractmethod
    def predict(self, prompt: str, **kwargs):
        pass

   