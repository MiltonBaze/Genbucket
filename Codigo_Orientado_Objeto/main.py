import sys
import json
from genbucket.core import GenBucket

def main():
    # Permite usar config_gpt.json, config_lstm.json ou config_transformer.json
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config_gpt.json"

    try:
        app = GenBucket(config_path)
        app.executar()
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
