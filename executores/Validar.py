import os
import argparse
import requests
import SeparadorFuncoes as sep

def validar_buckets(prompt_dir, catalogados_dir, versao):
    arquivo_filtrado = os.path.join(prompt_dir, f"V_{versao}", f"Saida{versao}_Filtrado.txt")
    pasta_catalogados = os.path.join(catalogados_dir, f"V_{versao}")
    os.makedirs(pasta_catalogados, exist_ok=True)

    sep.modoSaida = "a"
    sep.diretorioSaida = pasta_catalogados + "/"
    sep.init()

    if not os.path.exists(arquivo_filtrado):
        print(f"❌ Arquivo de buckets filtrados não encontrado: {arquivo_filtrado}")
        return

    endpoints = [
        ".s3.amazonaws.com",
        ".storage.googleapis.com",
        ".fra1.digitaloceanspaces.com",
        ".nyc3.digitaloceanspaces.com",
        ".sgp1.digitaloceanspaces.com",
        ".ams3.digitaloceanspaces.com"
    ]

    with open(arquivo_filtrado, "r", encoding="utf-8") as entrada:
        for i, bucket in enumerate(entrada, start=1):
            bucket = bucket.strip()
            if not bucket:
                continue

            try:
                for endpoint in endpoints:
                    url = f"https://{bucket}{endpoint}"
                    try:
                        response = requests.head(url, timeout=10)
                        status = response.status_code
                    except requests.exceptions.RequestException as e:
                        sep.outros(bucket, url, f"Erro de rede: {str(e)}")
                        continue

                    if status == 200:
                        sep.publico(bucket, url)
                    elif status == 403:
                        sep.privado(bucket, url)
                    elif status == 404:
                        sep.notFound(bucket, url)
                    elif status == 400:
                        sep.outros(bucket, url, "Nome de bucket inválido")
                    else:
                        sep.outros(bucket, url, status)

                    print(f"{i} - {bucket} - {status} - {url}")

            except KeyboardInterrupt:
                print("❌ Execução interrompida pelo usuário.")
                break
            except Exception as e:
                sep.outros(bucket, url, f"Erro inesperado: {str(e)}")
                continue

    sep.newsBuckets()
    sep.arqClose()
    print(f"✅ Validação da versão {versao} concluída.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validador de buckets gerados por modelos.")
    parser.add_argument("--modelo", required=True, help="Nome do modelo usado (ex: lstm, gpt, transformer)")
    parser.add_argument("--versao", nargs="+", required=True,
                        help="Versão(ões) da geração (ex: 1 2 3 ou 'all')")

    args = parser.parse_args()

    prompt_dir = os.path.join("resultados", args.modelo, "prompts")
    catalogados_dir = os.path.join("resultados", args.modelo, "catalogados")

    # Verifica se é 'all' ou lista de versões específicas
    if "all" in args.versao:
        versoes = list(range(1, 11))  # V1 até V10
    else:
        versoes = [int(v) for v in args.versao]

    for v in versoes:
        validar_buckets(prompt_dir, catalogados_dir, v)
