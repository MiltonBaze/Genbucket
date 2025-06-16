import os
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse

class AnalisadorConteudoBuckets:
    def __init__(self, base_dir, extensoes_desejadas=None):
        self.base_dir = base_dir
        self.catalogados_dir = os.path.join(base_dir, 'Catalogados')
        self.extensoes_desejadas = extensoes_desejadas or {
            "js", "mjs", "cjs", "jsx", "ts", "tsx", "xml",
            "json", "html", "php", "asp", "aspx", "jsp", "svg"
        }

    def extrair_provedor(self, bucket_url):
        if "s3" in bucket_url:
            return "s3"
        elif "storage" in bucket_url:
            return "google"
        elif "digitaloceanspaces" in bucket_url:
            return "digitalocean"
        return "desconhecido"

    def contar_extensoes(self, caminho_pasta, arquivo_saida, arquivo_buckets):
        contagem = defaultdict(int)
        tamanho_total = defaultdict(int)
        buckets = defaultdict(lambda: defaultdict(int))
        extensoes_total = Counter()

        for arquivo_nome in os.listdir(caminho_pasta):
            if arquivo_nome.endswith('.txt'):
                caminho_arquivo = os.path.join(caminho_pasta, arquivo_nome)
                with open(caminho_arquivo, 'r', encoding='utf-8', errors='replace') as arquivo:
                    for linha in arquivo:
                        linha = linha.strip()
                        if "http" in linha:
                            match = re.search(r'(https?://[^\s>]+)', linha)
                            if match:
                                url = match.group(1)
                                caminho_url = urlparse(url).path
                                nome_arquivo = os.path.basename(caminho_url)
                                if '.' in nome_arquivo:
                                    _, ext = os.path.splitext(nome_arquivo)
                                    ext = ext[1:].lower()
                                    extensoes_total[ext] += 1
                                    if ext in self.extensoes_desejadas:
                                        contagem[ext] += 1
                                        tamanho_total[ext] += 0  # Simulado
                                        bucket_host = urlparse(url).netloc
                                        provedor = self.extrair_provedor(bucket_host)
                                        buckets[(bucket_host, provedor)][ext] += 1
                                        buckets[(bucket_host, provedor)]["tamanho"] += 0

        os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

        with open(arquivo_saida, "w", encoding="utf-8") as f:
            for ext in sorted(contagem.keys()):
                f.write(f"{ext}: {contagem[ext]} arquivos\n")

        with open(arquivo_buckets, "w", encoding="utf-8") as f:
            for (bucket, provedor), dados in buckets.items():
                f.write(f"{bucket} - provedor {provedor}:\n")
                for ext, count in dados.items():
                    if ext != "tamanho":
                        f.write(f"  {ext}: {count} arquivos\n")

        caminho_extensoes = os.path.join(os.path.dirname(arquivo_saida), "extensoes_contagem.txt")
        with open(caminho_extensoes, "w", encoding="utf-8") as f:
            f.write("Contagem de extensões encontradas:\n\n")
            f.write(">> Extensões desejadas:\n")
            for ext in sorted(self.extensoes_desejadas):
                f.write(f"{ext}: {extensoes_total.get(ext, 0)}\n")
            f.write("\n>> Outras extensões encontradas:\n")
            for ext, count in sorted(extensoes_total.items()):
                if ext not in self.extensoes_desejadas:
                    f.write(f"{ext}: {count}\n")

        print(f"[OK] Pasta {caminho_pasta} analisada.")
        print(f"→ Salvos: resultado.txt, buckets.txt e extensoes_contagem.txt.")

    def analisar_todos(self):
        for nome_versao in sorted(os.listdir(self.catalogados_dir)):
            caminho_versao = os.path.join(self.catalogados_dir, nome_versao)
            caminho_publico = os.path.join(caminho_versao, 'ConteudoPublico')

            if os.path.isdir(caminho_publico) and nome_versao.lower().startswith('v_'):
                numero_versao = nome_versao.replace('V_', '').replace('v_', '')
                pasta_resultado = os.path.join(caminho_versao, f'Resultado_AnaliseV{numero_versao}')
                arquivo_saida = os.path.join(pasta_resultado, 'resultado.txt')
                arquivo_buckets = os.path.join(pasta_resultado, 'buckets.txt')

                self.contar_extensoes(caminho_publico, arquivo_saida, arquivo_buckets)
