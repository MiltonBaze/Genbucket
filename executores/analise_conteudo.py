import os
import re
from urllib.parse import urlparse
from collections import defaultdict, Counter

def analise_conteudo(self):
    modelo = self.config.get("modelo", "desconhecido")
    print(f"🔍 Iniciando análise de conteúdo dos buckets ({modelo})...")

    extensoes_desejadas = {
        "js", "mjs", "cjs", "jsx", "ts", "tsx", "xml",
        "json", "html", "php", "asp", "aspx", "jsp", "svg"
    }

    catalogados_dir = self.catalogados_dir

    if not os.path.isdir(catalogados_dir):
        print(f"❌ Diretório não encontrado: {catalogados_dir}")
        return

    for nome_versao in sorted(os.listdir(catalogados_dir)):
        caminho_versao = os.path.join(catalogados_dir, nome_versao)
        caminho_publico = os.path.join(caminho_versao, "ConteudoPublico")

        if os.path.isdir(caminho_publico) and nome_versao.lower().startswith('v_'):
            numero_versao = nome_versao.lower().replace('v_', '')
            pasta_resultado = os.path.join(caminho_versao, f'Resultado_AnaliseV{numero_versao}')
            arquivo_saida = os.path.join(pasta_resultado, 'resultado.txt')
            arquivo_buckets = os.path.join(pasta_resultado, 'buckets.txt')
            caminho_extensoes = os.path.join(pasta_resultado, 'extensoes_contagem.txt')

            contagem = defaultdict(int)
            tamanho_total = defaultdict(int)
            buckets = defaultdict(lambda: defaultdict(int))
            extensoes_total = Counter()

            for nome_arquivo in os.listdir(caminho_publico):
                if not nome_arquivo.endswith('.txt'):
                    continue

                caminho_arquivo = os.path.join(caminho_publico, nome_arquivo)
                with open(caminho_arquivo, 'r', encoding='utf-8', errors='replace') as arquivo:
                    for linha in arquivo:
                        linha = linha.strip()
                        if "http" not in linha:
                            continue

                        match = re.search(r'(https?://[^\s>]+)', linha)
                        if not match:
                            continue

                        url = match.group(1)
                        caminho_url = urlparse(url).path
                        nome_arquivo_url = os.path.basename(caminho_url)

                        if '.' not in nome_arquivo_url:
                            continue

                        _, ext = os.path.splitext(nome_arquivo_url)
                        ext = ext[1:].lower()

                        extensoes_total[ext] += 1

                        if ext in extensoes_desejadas:
                            contagem[ext] += 1
                            tamanho_total[ext] += 0  # sem uso por enquanto
                            bucket_host = urlparse(url).netloc

                            if "s3" in bucket_host:
                                provedor = "s3"
                            elif "storage" in bucket_host:
                                provedor = "google"
                            elif "digitaloceanspaces" in bucket_host:
                                provedor = "digitalocean"
                            else:
                                provedor = "desconhecido"

                            buckets[(bucket_host, provedor)][ext] += 1
                            buckets[(bucket_host, provedor)]["tamanho"] += 0

            os.makedirs(pasta_resultado, exist_ok=True)

            with open(arquivo_saida, "w", encoding="utf-8") as f:
                for ext in sorted(contagem.keys()):
                    f.write(f"{ext}: {contagem[ext]} arquivos\n")

            with open(arquivo_buckets, "w", encoding="utf-8") as f:
                for (bucket, provedor), dados in buckets.items():
                    f.write(f"{bucket} - provedor {provedor}:\n")
                    for ext, count in dados.items():
                        if ext != "tamanho":
                            f.write(f"  {ext}: {count} arquivos\n")

            with open(caminho_extensoes, "w", encoding="utf-8") as f:
                f.write("Contagem de extensões encontradas:\n\n")
                f.write(">> Extensões desejadas:\n")
                for ext in sorted(extensoes_desejadas):
                    f.write(f"{ext}: {extensoes_total.get(ext, 0)}\n")

                f.write("\n>> Outras extensões encontradas:\n")
                for ext, count in sorted(extensoes_total.items()):
                    if ext not in extensoes_desejadas:
                        f.write(f"{ext}: {count}\n")

            print(f"[✓] Pasta '{caminho_publico}' analisada.")
            print(f"   ↳ {arquivo_saida}")
            print(f"   ↳ {arquivo_buckets}")
            print(f"   ↳ {caminho_extensoes}")

    print("✅ Análise de conteúdo dos buckets finalizada.")
