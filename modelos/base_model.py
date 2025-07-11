from abc import ABC, abstractmethod

class BaseModel(ABC):
 #   @abstractmethod
 #   def validar_dataset(self):
 #       pass
    
    @abstractmethod
    def fit(self, dataset_path: str):
        pass

    @abstractmethod
    def predict(self, prompt: str, **kwargs):
        pass

   # @abstractmethod
   # def validar_buckets(self, prompt_dir, catalogados_dir, versao):
    #    pass

   # @abstractmethod
   # def verificar_buckets_publicos(self, config):
   #     pass

   # @abstractmethod
   # def analise_conteudo(self):
   #     pass
    
   # @abstractmethod
   # def analisar_vulnerabilidades(config):
   #     pass
    
   # @abstractmethod
   # def analisar_vulnerabilidades(config):
   #     pass