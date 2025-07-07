
python main.py
------------------------------------------------------------------
Maneira individualizada
validar dataset(Opcional)
python executores/validador_dataset.py dados/buckets.txt
---------------------------------------------------------------------
treinar
python executores/treinamento.py --config config_lstm.json --dataset dados/buckets_validado.txt
python executores/treinamento.py --config config_gpt.json --dataset dados/buckets_validado.txt
python executores/treinamento.py --config config_transformer.json --dataset dados/buckets_validado.txt
------------------------------------------------------------------
Gerar nomes de Buckets pelos modelos
python executores/gerar.py --config config_lstm.json
python executores/gerar.py --config config_gpt.json
python executores/gerar.py --config config_transformer.json

----------------------------------------------------------------
Validar nomes de buckets gerados pelos modelos nos provedores
python executores/validar.py --modelo lstm --versao 1
python executores/validar.py --modelo gptneo --versao 1
python executores/validar.py --modelo transformer --versao 1
python executores/validar.py --modelo lstm --versao all

----------------------------------------------------
Verificar buckets publicos e privados e separa-los
python executores/verificar_buckets_publicos.py  --config config_gpt.json
python executores/verificar_buckets_publicos.py  --config config_lstm.json
python executores/verificar_buckets_publicos.py  --config config_transformer.json
----------------------------------------------------------------------------------
Analise_conteudo encontrados nos buckets publicos
python executores/analise_conteudo.py --config config_gpt.json
python executores/analise_conteudo.py --config config_lstm.json
python executores/analise_conteudo.py --config config_transformer.json

----------------------------------------------------------
Analise de vulnerabilidades nos buckets publicos V1 - Wapiti - Nuclei openSource 
python executores/analisar_vulnerabilidades.py --config config_lstm.json
python executores/analisar_vulnerabilidades.py --config config_gpt.json
python executores/analisar_vulnerabilidades.py --config config_transformer.json


