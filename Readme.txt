#  GenBucket

**GenBucket** is a modular tool for generating and validating cloud bucket names with modern generative models. GENBUCKET supports LSTM, Transformer, and GPT, trained with customizable datasets to capture different naming patterns.
The tool automatically generates candidate names, verifies their existence via DNS, classifies them via HTTP, and analyzes public buckets for vulnerabilities.
-------------------------------------------------------------------------------------------------------------------------------------------

##  Installation

### 1. Install the dependencies
pip install -r requirements.txt

-------------------------------------------------
## settings

All parameters are set via config_[MODEL].json

Exemplo:

{
  "model": "lstm",
  "dataset_path": "data/dataset.txt",
  "output_dir": "Result/LSTM/",
  "num_return_sequences": 10,
  "max_length": 60,
  "temperature": 1.0
}
-----------------------------------------------------------
External Requirements

Some tools are required outside of Python. 
Install them manually:

                     Tool                    Installation Instructions
| Ambiente    | Nuclei                     | Wapiti                       |
| ----------- | -------------------------- | ---------------------------- |
| **Windows** | `tools/nuclei.exe`         | `tools/wapiti.exe`           |
| **Linux**   | `tools/nuclei` (Linux bin) | tools/wapiti - Instalar via  |
					   | `pip` ou script              |

OBS:The Nuclei and Wapiti executables are located in the tools/ folder on Windows (as .exe) - you need to extract it.
Wapiti pip install wapiti3 or download - git clone https://github.com/wapiti-scanner/wapiti
Download Nuclei release and add it to your PATH.
https://github.com/projectdiscovery/nuclei/releases


--------------------------------------------------------------
## How to use

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
--------------------------------------------------------------------------------------------------------------------------------------------------
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


