#  _GenBucket_

**GenBucket** is a modular tool for generating and validating cloud bucket names with modern generative models. GENBUCKET supports LSTM, Transformer, and GPT, trained with customizable datasets to capture different naming patterns.
The tool automatically generates candidate names, verifies their existence via DNS, classifies them via HTTP, and analyzes public buckets for vulnerabilities.
------------------------------------------------------------------------------------------------------------------------------

## 1. Installation - Pynthon 3.12
------------------------------------------------------------------------------------------------------------------------------

## 2. https://github.com/MiltonBaze/Genbucket
   Code: Download ZIP: Genbucket-main.zip

------------------------------------------------------------------------------------------------------------------------------
## 3. External Requirements

Folder: Tools: Unzip the 2 files: NUCLEI.rar e WAPITI.rar

https://wapiti-scanner.github.io/
https://github.com/wapiti-scanner/wapiti
https://github.com/wapiti-scanner/wapiti/releases
wapiti3-3.2.3-py3-none-any.whl
wapiti3-3.2.3.tar.gz
3.2.3.zip

https://github.com/projectdiscovery/nuclei
https://github.com/projectdiscovery/nuclei/releases
nuclei_3.4.7_windows_amd64.zip
------------------------------------------------------------------------------------------------------------------------------

## 4. create and activate the project's virtual environment:

python -m venv venv 

source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

-------------------------------------------------------------------------------------------------------------------------------

## 5. Install the dependencies


install : pip install -r requirements.txt
install : pip install library_name


-------------------------------------------------------------------------------------------------------------------------------
## 6. settings

All parameters are set via config_[MODEL].json

Example:

{
  "model": "lstm",
  "dataset_path": "data/dataset.txt",
  "output_dir": "Result/LSTM/",
  "num_return_sequences": 10,
  "max_length": 60,
  "temperature": 1.0
}
----------------------------------------------------------------------------------------------------------------------------

## 7. How to use

VIA main.py - (Parameters passed by config_model.json)
Any changes to the model configuration must be made in config.json
Models:

LSTM
python main.py --acao 1 --config config_lstm.json     # Validate the dataset
python main.py --acao 2 --config config_lstm.json     # Train the chosen model
python main.py --acao 3 --config config_lstm.json     # Generate Bucket Names
python main.py --acao 4 --config config_lstm.json     # Validates the generated bucket names
python main.py --acao 5 --config config_lstm.json     # Separates public and private buckets
python main.py --acao 6 --config config_lstm.json     # analyze_content of public buckets
python main.py --acao 7 --config config_lstm.json     # analyze vulnerabilities of objects with external programs (Wapiti/Nuclei open source)
python main.py --acao 8 --config config_lstm.json     # analyze_vulnerabilities of objects with external programs (Qualys/Nessus-Pro)
python main.py --acao 9 --config config_lstm.json     # Executes the complete program pipeline
----------------------------------------------------------------------------------------------------------------------------------------------
GPT-NEO
python main.py --acao 1 --config config_gpt.json     # Validate the dataset
python main.py --acao 2 --config config_gpt.json     # Train the chosen model
python main.py --acao 3 --config config_gpt.json     # Generate Bucket Names
python main.py --acao 4 --config config_gpt.json     # Validates the generated bucket names
python main.py --acao 5 --config config_gpt.json     # Separates public and private buckets
python main.py --acao 6 --config config_gpt.json     # analyze_content of public buckets
python main.py --acao 7 --config config_gpt.json     # analyze vulnerabilities of objects with external programs (Wapiti/Nuclei open source)
python main.py --acao 8 --config config_gpt.json     # analyze_vulnerabilities of objects with external programs (Qualys/Nessus-Pro)
python main.py --acao 9 --config config_gpt.json     # Executes the complete program pipeline
---------------------------------------------------------------------------------------------------------------------------------------------------
TRANSFORMER
python main.py --acao 1 --config config_transformer.json     # Validate the dataset
python main.py --acao 2 --config config_transformer.json     # Train the chosen model
python main.py --acao 3 --config config_transformer.json     # Generate Bucket Names
python main.py --acao 4 --config config_transformer.json     # Validates the generated bucket names
python main.py --acao 5 --config config_transformer.json     # Separates public and private buckets
python main.py --acao 6 --config config_transformer.json     # analyze_content of public buckets
python main.py --acao 7 --config config_transformer.json     # analyze vulnerabilities of objects with external programs (Wapiti/Nuclei open source)
python main.py --acao 8 --config config_transformer.json     # analyze_vulnerabilities of objects with external programs (Qualys/Nessus-Pro)
python main.py --acao 9 --config config_transformer.json     # Executes the complete program pipeline
------------------------------------------------------------------------------------------------------------


