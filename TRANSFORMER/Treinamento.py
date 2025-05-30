# Import configuração com parametros da IA
import config6_1 as config
# Import de Classes usadas no treinamento
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling, TrainingArguments, Trainer

# Carregar o modelo GPT-Neo e o tokenizer do GPT2
modelo = GPTNeoForCausalLM.from_pretrained(config.model_name)
tokenizer = GPT2Tokenizer.from_pretrained(config.model_name)

# Carregar a base de dados de texto com os nomes
baseDeTreinamento = TextDataset(
    tokenizer=tokenizer, # Instancia do tokenizer
    file_path=config.file_path, # Arquivo de entrada
    block_size=config.block_size  # Ajuste o tamanho do bloco conforme necessário
)

# Criar um data collator para formatar os dados
dados_formatados = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Definir argumentos de treinamento
argumentos_treinamento = TrainingArguments(
    output_dir=config.output_dir, # Qual diretório de saida
    overwrite_output_dir=config.overwrite_output_dir, # Se deve sobreescrever o diretorio
    num_train_epochs=config.num_train_epochs,  # Ajuste o número de épocas conforme necessário
    per_device_train_batch_size=config.per_device_train_batch_size # Define o paralelismo do treinamento
)

# Criar o Trainer e iniciar o treinamento
treinamento = Trainer(
    model=modelo,
    args=argumentos_treinamento,
    data_collator=dados_formatados,
    train_dataset=baseDeTreinamento,
)

# Iniciar o treinamento
treinamento.train()

# Salvar o modelo treinado
treinamento.save_model(config.save_model)
