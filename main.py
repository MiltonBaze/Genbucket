import os
import sys
import json
import requests
import subprocess

# Variáveis globais
dataset_escolhido = None
modelo_escolhido = None
buckets_validados = []
arquivo_gerados = "buckets_gerados.txt"
arquivo_validados = "buckets_validados.txt"

# Carrega parâmetros do JSON passado como argumento
def carregar_configuracao(config_path="config.json"):
    if not os.path.exists(config_path):
        print(f"❌ Arquivo de configuração '{config_path}' não encontrado.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def verificar_dataset_valido(caminho):
    return os.path.exists(caminho) and caminho.lower().endswith(('.csv', '.txt'))

def validar_buckets_do_dataset(caminho):
    buckets_validos = []
    endPointList = [
        '.s3.amazonaws.com',
        '.storage.googleapis.com',
        '.fra1.digitaloceanspaces.com',
        '.nyc3.digitaloceanspaces.com',
        '.sgp1.digitaloceanspaces.com',
        '.ams3.digitaloceanspaces.com'
    ]

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    for linha in linhas:
        bucket = linha.strip()
        for endpoint in endPointList:
            url = f"https://{bucket}{endpoint}"
            try:
                response = requests.head(url, timeout=3)
                status = response.status_code

                if status in [200, 403]:
                    print(f"[✔] Bucket encontrado: {bucket} ({status}) - {url}")
                    buckets_validos.append(bucket)
                    break
                elif status == 404:
                    print(f"[✖] Não encontrado: {bucket}")
                elif status == 400:
                    print(f"[!] Nome inválido: {bucket}")
                else:
                    print(f"[?] Status {status} para {bucket}")
            except Exception as e:
                print(f"[!] Erro ao verificar {bucket}: {e}")
    return buckets_validos

def executar_validador_e_verificador(validador_path, verificador_path):
    try:
        print("Executando validador de buckets...")
        subprocess.run(["python", validador_path], check=True)
        print("✅ Validação concluída.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o validador: {e}")

    try:
        print("Executando verificador de buckets públicos...")
        subprocess.run(["python", verificador_path], check=True)
        print("✅ Verificação de conteúdo concluída.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o verificador: {e}")

def executar_analise_publicos(script_analise):
    subprocess.run(["python", script_analise], check=True)

def executar_modelo_externo(modelo, dataset_path):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "GenBucket"))

    scripts = {
        "LSTM": os.path.join(base_path, "LSTM", "LSTM.py"),
        "LSTM_VALIDACAO": os.path.join(base_path, "LSTM", "validador_buckets.py"),
        "LSTM_VERIFICACAO": os.path.join(base_path, "LSTM", "verificadorBucketspublicos.py"),
        "LSTM_ANALISA_PUBLICOS": os.path.join(base_path, "LSTM", "Analisa_Publico.py"),
        "LSTM_ANALISE_FERRAMENTAS": os.path.join(base_path, "LSTM", "Analise_Vulnerabilidades.py"),

        "GPT_NEO_TREINAMENTO": os.path.join(base_path, "GPT_neo", "Treinamento.py"),
        "GPT_NEO_GERADOR": os.path.join(base_path, "GPT_neo", "GPT_Gerador.py"),
        "GPT_NEO_VALIDACAO": os.path.join(base_path, "GPT_neo", "validador_buckets.py"),
        "GPT_NEO_VERIFICACAO": os.path.join(base_path, "GPT_neo", "verificadorBucketspublicos.py"),
        "GPT_NEO_ANALISA_PUBLICOS": os.path.join(base_path, "GPT_neo", "Analisa_Publico.py"),
        "GPT_NEO_ANALISE_FERRAMENTAS": os.path.join(base_path, "GPT_neo", "Analise_Vulnerabilidades.py"),

        "TRANSFORMER": os.path.join(base_path, "TRANSFORMER", "transformer.py"),
        "TRANSFORMER_VALIDACAO": os.path.join(base_path, "TRANSFORMER", "validador_buckets.py"),
        "TRANSFORMER_VERIFICACAO": os.path.join(base_path, "TRANSFORMER", "verificadorBucketspublicos.py"),
        "TRANSFORMER_ANALISA_PUBLICOS": os.path.join(base_path, "TRANSFORMER", "Analisa_Publico.py"),
        "TRANSFORMER_ANALISE_FERRAMENTAS": os.path.join(base_path, "TRANSFORMER", "Analise_Vulnerabilidades.py"),
    }

    try:
        if modelo == "GPT_NEO":
            subprocess.run(["python", scripts["GPT_NEO_TREINAMENTO"], dataset_path], check=True)
            subprocess.run(["python", scripts["GPT_NEO_GERADOR"], dataset_path], check=True)
            executar_validador_e_verificador(scripts["GPT_NEO_VALIDACAO"], scripts["GPT_NEO_VERIFICACAO"])
            executar_analise_publicos(scripts["GPT_NEO_ANALISA_PUBLICOS"])
            executar_analise_publicos(scripts["GPT_NEO_ANALISE_FERRAMENTAS"])

        elif modelo == "TRANSFORMER":
            subprocess.run(["python", scripts["TRANSFORMER"], dataset_path], check=True)
            executar_validador_e_verificador(scripts["TRANSFORMER_VALIDACAO"], scripts["TRANSFORMER_VERIFICACAO"])
            executar_analise_publicos(scripts["TRANSFORMER_ANALISA_PUBLICOS"])
            executar_analise_publicos(scripts["TRANSFORMER_ANALISE_FERRAMENTAS"])

        elif modelo == "LSTM":
            subprocess.run(["python", scripts["LSTM"], dataset_path], check=True)
            executar_validador_e_verificador(scripts["LSTM_VALIDACAO"], scripts["LSTM_VERIFICACAO"])
            executar_analise_publicos(scripts["LSTM_ANALISA_PUBLICOS"])
            executar_analise_publicos(scripts["LSTM_ANALISE_FERRAMENTAS"])

        else:
            print(f"❌ Modelo '{modelo}' não reconhecido.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o script do modelo {modelo}: {e}")

def salvar_em_arquivo(nome_arquivo, lista):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in lista:
            f.write(item + "\n")

def rodar_codigo():
    if not dataset_escolhido or not modelo_escolhido:
        print("❌ Você precisa fornecer 'dataset_path' e 'modelo' no JSON.")
        return

    print(f"\n🚀 Executando modelo '{modelo_escolhido}' com dataset '{dataset_escolhido}'...")
    executar_modelo_externo(modelo_escolhido, dataset_escolhido)

    if os.path.exists(arquivo_gerados):
        print(f"\n✅ Buckets gerados foram salvos em: {arquivo_gerados}")
    else:
        print("⚠️ Nenhum bucket gerado foi encontrado.")

def executar_modo_automatico():
    global dataset_escolhido, modelo_escolhido, buckets_validados

    dataset_escolhido = config.get("dataset_path")
    modelo_escolhido = config.get("modelo")

    if not dataset_escolhido or not modelo_escolhido:
        print("❌ Configuração JSON incompleta. Use 'dataset_path' e 'modelo'.")
        return

    if not verificar_dataset_valido(dataset_escolhido):
        print(f"❌ Dataset inválido ou extensão não suportada: {dataset_escolhido}")
        return

    print(f"✅ Dataset: {dataset_escolhido}")
    print(f"✅ Modelo: {modelo_escolhido}")

    if config.get("validar_buckets", False):
        print("🔍 Validando buckets...")
        buckets_validados = validar_buckets_do_dataset(dataset_escolhido)
        salvar_em_arquivo(arquivo_validados, buckets_validados)
        print(f"✅ {len(buckets_validados)} buckets válidos salvos em '{arquivo_validados}'")

    rodar_codigo()

# 🚀 Início do programa (modo automático direto)
if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    config = carregar_configuracao(config_file)
    executar_modo_automatico()
