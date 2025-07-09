Maneira individualizada 
------------------------------------------------------------------
1 - Validar dataset(Opcional)
python executores/validador_dataset.py dados/buckets.txt
---------------------------------------------------------------------
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
4 - Validar nomes de buckets gerados pelos modelos nos provedores
python executores/validar.py --modelo lstm --versao 1 ou 2 ou 3...10
python executores/validar.py --modelo gptneo --versao 1 ou 2 ou 3...10
python executores/validar.py --modelo transformer --versao 1 ou 2 ou 3...10

python executores/validar.py --modelo lstm --versao all

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
python executores/analise_conteudo.py --config config_lstm.json

----------------------------------------------------------
7 - Analise de vulnerabilidades nos buckets publicos V1 - Wapiti - Nuclei openSource 
python executores/analise_vulnerabilidades_v1.py --config config_lstm.json
python executores/analisar_vulnerabilidades_v1.py --config config_gpt.json
python executores/analisar_vulnerabilidades_v1.py --config config_transformer.json

---------------------------------------------------------------------------------------
8 - Analise de vulnerabilidades nos buckets publicos V2 - Qualys - Nessus pro 

python executores/analise_vulnerabilidades_v2.py --config config_lstm.json
python executores/analisar_vulnerabilidades_v2.py --config config_gpt.json
python executores/analisar_vulnerabilidades_v2.py --config config_transformer.json



