import os
import re
from datetime import datetime
from Ferramentas_Vuln import executar_wapiti, executar_nuclei


class VerificadorVulnerabilidades:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.catalogado_dir = os.path.join(base_dir, "Catalogados")
        self.relatorios_dir = os.path.join(self.catalogado_dir, "relatorios")
        os.makedirs(self.relatorios_dir, exist_ok=True)

    def ler_buckets_txt(self, caminho_arquivo):
        buckets = []
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                match = re.match(r'^(.*?) - provedor (\w+):$', linha)
                if match:
                    bucket_url = match.group(1).strip()
                    provedor = match.group(2).strip()
                    buckets.append((bucket_url, provedor))
        return buckets

    def rodar_analises_vulnerabilidade(self, bucket_url):
        url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
        print(f"\n🔍 Analisando: {url}")
        resultado = f"Bucket: {bucket_url}\n"

        try:
            nome_bucket = bucket_url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
            saida_html = os.path.join(self.relatorios_dir, f"{nome_bucket}_wapiti.html")
            print(" ▶ Executando Wapiti...")
            executar_wapiti(url, saida_html)
            resultado += f"  ✅ Wapiti: {saida_html}\n"
        except Exception as e:
            resultado += f"  ❌ Wapiti falhou: {e}\n"

        try:
            print(" ▶ Executando Nuclei...")
            executar_nuclei(url)
            resultado += f"  ✅ Nuclei: executado com sucesso\n"
        except Exception as e:
            resultado += f"  ❌ Nuclei falhou: {e}\n"

        return resultado

    def salvar_relatorio(self, linhas, saida_path):
        with open(saida_path, 'w', encoding='utf-8') as f:
            for linha in linhas:
                f.write(linha + "\n")
        print(f"\n📝 Relatório salvo em: {saida_path}")

    def analisar_todos(self):
        relatorio_final = []

        for versao in sorted(os.listdir(self.catalogado_dir)):
            if versao.lower().startswith("v_"):
                resultado_path = os.path.join(
                    self.catalogado_dir,
                    versao,
                    f"Resultado_AnaliseV{versao[2:]}",
                    "buckets.txt"
                )

                if os.path.exists(resultado_path):
                    print(f"\n📂 Processando: {resultado_path}")
                    buckets = self.ler_buckets_txt(resultado_path)

                    for bucket_url, provedor in buckets:
                        resumo = self.rodar_analises_vulnerabilidade(bucket_url)
                        relatorio_final.append(resumo)
                else:
                    print(f"⚠️ Arquivo não encontrado: {resultado_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_saida = os.path.join(self.base_dir, f"Relatorio_Wapiti_Nuclei_{timestamp}.txt")
        self.salvar_relatorio(relatorio_final, caminho_saida)
