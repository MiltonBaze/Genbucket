validar dataset
python executores/validador_dataset.py dados/buckets.txt
-------------------------------------------------
treinar
python executores/treinamento.py --config config_lstm.json --dataset dados/buckets_validado.txt

------------------------------------------------------------------
Gerar
python executores/gerar.py --config config_lstm.json

----------------------------------------------------------------
validar
python executores/validador.py --modelo lstm --versao 1
python executores/validador.py --modelo lstm --versao all

----------------------------------------------------
verificar buckets publicos
python executores/verificar_buckets_publicos.py --config config_gpt.json
python executores/verificar_buckets_publicos.py --config config_lstm.json
------------------------------------------------------------------------------
Analisar - Programas Externo
python executores/analise_vulnerabilidade_v1.py --config config_gpt.json
python executores/analise_vulnerabilidade_v1.py --config config_lstm.json
python executores/analise_vulnerabilidade_v1.py --config config_transformer.json

------------------------------------------------------------------------------

