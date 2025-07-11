import argparse
import os
import sys
import json

def carregar_config(caminho_config):
    if not os.path.exists(caminho_config):
        print(f"❌ Arquivo de configuração não encontrado: {caminho_config}")
        sys.exit(1)
    with open(caminho_config, "r", encoding="utf-8") as f:
        return json.load(f)

def substituir_variaveis(comando, config_path, config):
    return (
        comando.replace("CONFIG", config_path)
               .replace("DATASET", config.get("dataset_path", ""))
               .replace("MODELO", config.get("modelo", ""))
               .replace("VERSAO", str(config.get("validar_versoes", "all")))
    )

def executar_comando(codigo, config_path, config):
    comandos_json = config.get("comandos", {})
    
    if codigo == 9:
        print("▶ Executando pipeline completo...")
        for i in range(1, 9):
            cmd_str = comandos_json.get(str(i))
            if cmd_str:
                cmd = substituir_variaveis(cmd_str, config_path, config)
                print(f"\n🟢 Etapa {i}: {cmd}")
                os.system(cmd)
            else:
                print(f"⚠️ Comando {i} não definido no JSON.")
    else:
        cmd_str = comandos_json.get(str(codigo))
        if not cmd_str:
            print(f"❌ Comando {codigo} não definido no JSON.")
            return
        cmd = substituir_variaveis(cmd_str, config_path, config)
        print(f"▶ Executando: {cmd}")
        os.system(cmd)

def main():
    parser = argparse.ArgumentParser(description="Executor GenBucket via parâmetros.")
    parser.add_argument("--acao", type=int, required=True, help="Código da ação a ser executada (1-9)")
    parser.add_argument("--config", type=str, required=True, help="Caminho para o arquivo config.json")
    global args
    args = parser.parse_args()

    config = carregar_config(args.config)
    executar_comando(args.acao, args.config, config)

if __name__ == "__main__":
    main()
