from executores import ( validador_dataset, 
    treinamento, gerar, Validar,
    verificar_buckets_publicos,
    analise_conteudo,
    analise_vulnerabilidade_v1
)

import sys

def executar_pipeline(config_path):
    
    sys.argv = ["", "--config", config_path]

    print(f"\n📦 Rodando pipeline para: {config_path}")

    print("🚀 Validar Dataset...")
    validador_dataset.main()
    
    print("🚀 Treinando...")
    treinamento.main()

    print("🧠 Gerando nomes...")
    gerar.main()

    print("✅ Validando nomes...")
    Validar.main()

    print("🌐 Verificando buckets públicos...")
    verificar_buckets_publicos.main()

    print("📂 Analisando conteúdo dos buckets...")
    analise_conteudo.main()

    print("🛡️ Analisando vulnerabilidades...")
    analise_vulnerabilidade_v1.main()

    print(f"🎉 Finalizado: {config_path}\n" + "="*60)


if __name__ == "__main__":
    # Rode para múltiplos modelos:
    executar_pipeline("config_lstm.json")
    executar_pipeline("config_gptneo.json")
    executar_pipeline("config_transformer.json")
