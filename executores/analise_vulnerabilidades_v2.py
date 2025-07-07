import sys
from GenBucket.config_loader import carregar_config
from GenBucket.model_selector import carregar_pipeline

def main():
    if len(sys.argv) < 2:
        print("Uso: python vulnerabilidades_local.py <nome_do_modelo>")
        return

    modelo = sys.argv[1]
    print(f"📦 Carregando config do modelo '{modelo}'...")

    try:
        config = carregar_config(modelo)
    except Exception as e:
        print(f"❌ Erro ao carregar a configuração: {e}")
        return

    print(f"⚠️ Iniciando análise de vulnerabilidades locais (Wapiti/Nuclei) com o modelo '{modelo}'...")

    try:
        pipeline = carregar_pipeline(modelo, config)
        pipeline.analyze_vulnerabilities_v1()
        print("✅ Análise de vulnerabilidades locais concluída com sucesso.")
    except Exception as e:
        print(f"❌ Erro durante a análise de vulnerabilidades locais: {e}")

if __name__ == "__main__":
    main()
