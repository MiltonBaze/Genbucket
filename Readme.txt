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

python executores/analisar_vulnerabilidades_api.py --config config_gpt.jso

