VIA main.py - (Parâmetros passados por config_modelo.json)

LSTM
python main.py --acao 1 --config config_lstm.json     # Valida o dataset
python main.py --acao 2 --config config_lstm.json     # Treina o modelo escolhido
python main.py --acao 3 --config config_lstm.json     # Gera Nomes Buckets
python main.py --acao 4 --config config_lstm.json     # Valida os nomes buckets gerados
python main.py --acao 5 --config config_lstm.json     # Separa os buckets publicos e privados
python main.py --acao 6 --config config_lstm.json     # analise_conteudo dos buckets públicos
python main.py --acao 7 --config config_lstm.json     # analise_vulnerabilidades dos objetos com programas externos(Wapiti/Nuclei open source)
python main.py --acao 8 --config config_lstm.json     # analise_vulnerabilidades dos objetos com programas externos(Qualys/Nessus-Pro)
python main.py --acao 9 --config config_lstm.json     # Executa pipeline completo do programa
--------------------------------------------------------------------------------------------------------------------------------------------------
GPT-NEO
python main.py --acao 1 --config config_gpt.json     # Valida o dataset
python main.py --acao 2 --config config_gpt.json     # Treina o modelo
python main.py --acao 3 --config config_gpt.json     # Gera Nomes Buckets
python main.py --acao 4 --config config_gpt.json     # Valida os buckets gerados
python main.py --acao 5 --config config_gpt.json     # Separa os buckets publicos e privados
python main.py --acao 6 --config config_gpt.json     # analise_conteudo dos buckets públicos
python main.py --acao 7 --config config_gpt.json     # analise_vulnerabilidades dos objetos com programas externos(Wapiti/Nuclei open source)
python main.py --acao 8 --config config_gpt.json     # analise_vulnerabilidades dos objetos com programas externos(Qualys/Nessus-Pro)
python main.py --acao 9 --config config_gpt.json     # Executa pipeline completo
---------------------------------------------------------------------------------------------------------------------------------------------------
TRANSFORMER
python main.py --acao 1 --config config_transformer.json     # Valida o dataset
python main.py --acao 2 --config config_transformer.json     # Treina o modelo
python main.py --acao 3 --config config_transformer.json     # Gera Nomes Buckets
python main.py --acao 4 --config config_transformer.json     # Valida os buckets gerados
python main.py --acao 5 --config config_transformer.json     # Separa os buckets publicos e privados
python main.py --acao 6 --config config_transformer.json     # analise_conteudo dos buckets públicos
python main.py --acao 7 --config config_transformer.json     # analise_vulnerabilidades dos objetos com programas externos(Wapiti/Nuclei open source)
python main.py --acao 8 --config config_transformer.json     # analise_vulnerabilidades dos objetos com programas externos(Qualys/Nessus-Pro)
python main.py --acao 9 --config config_transformer.json     # Executa pipeline completo 
------------------------------------------------------------------------------------------------------------------------------------------------------

Maneira individualizada 
------------------------------------------------------------------
1 - Validar dataset(Opcional)

python executores/validador_dataset.py --config config_lstm.json
python executores/validador_dataset.py --config config_gpt.json
python executores/validador_dataset.py --config config_transformer.json

--------------------------------------------------------------------
2 - Treinamento

python executores/treinamento.py --config config_lstm.json --dataset dados/buckets_validado.txt
python executores/treinamento.py --config config_gpt.json --dataset dados/buckets_validado.txt
python executores/treinamento.py --config config_transformer.json --dataset dados/buckets_validado.txt
------------------------------------------------------------------
3 - Gerar nomes de Buckets pelos modelos

python executores/gerar.py --config config_lstm.json
python executores/gerar.py --config config_gpt.json
python executores/gerar.py --config config_transformer.json

----------------------------------------------------------------
4 - Validar nomes de buckets gerados pelos modelos nos provedores por fases
config.modelo.json - "validar_versoes": "all", ou [1,2,3,4,5,6,7,8,9,10]

python executores/validar.py --config config_lstm.json
python executores/validar.py --config config_lstm.json
python executores/validar.py --config config_lstm.json

----------------------------------------------------
5 - Verificar buckets publicos e privados e separa-los

python executores/verificar_buckets_publicos.py  --config config_gpt.json
python executores/verificar_buckets_publicos.py  --config config_lstm.json
python executores/verificar_buckets_publicos.py  --config config_transformer.json
----------------------------------------------------------------------------------
6 - Analise_conteudo encontrados nos buckets publicos

python executores/analise_conteudo.py --config config_gpt.json
python executores/analise_conteudo.py --config config_lstm.json
python executores/analise_conteudo.py --config config_transformer.json

----------------------------------------------------------
7 - Analise de vulnerabilidades nos buckets publicos V1 - Wapiti - Nuclei open Source 

python executores/analise_vulnerabilidades_v1.py --config config_lstm.json
python executores/analisar_vulnerabilidades_v1.py --config config_gpt.json
python executores/analisar_vulnerabilidades_v1.py --config config_transformer.json

---------------------------------------------------------------------------------------
8 - Analise de vulnerabilidades nos buckets publicos V2 - Qualys - Nessus-pro 

python executores/analise_vulnerabilidades_v2.py --config config_lstm.json
python executores/analisar_vulnerabilidades_v2.py --config config_gpt.json
python executores/analisar_vulnerabilidades_v2.py --config config_transformer.json



