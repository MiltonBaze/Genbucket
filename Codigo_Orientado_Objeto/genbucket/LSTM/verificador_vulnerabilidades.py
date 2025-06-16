# verificador_vulnerabilidades.py

import os
import re
from datetime import datetime
from Ferramentas_Vuln import executar_wapiti, executar_nuclei


class VerificadorVulnerabilidadesLSTM:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.catalogado_dir = os.path.join(self.base_dir, "Catalogados")
        self.relatorios_dir = os.path.join(self.catalogado_dir, "relatorios")
        os.makedirs(self.relatorios_dir, exist_ok=True)
        self.relatorio_final = []

    def _ler_buckets_txt(self, caminho_arquivo):
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

    def _rodar_analises_vulnerabilidade(self, bucket_url):
        url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
        print(f"\n🔍 Analisando: {url}")
        resultado = f" Bucket: {bucket_url}\n"

        try:
            nome_bucket = bucket_url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
            saida_html = os.path.join(self.relatorios_dir, f"{nome_bucket}_wapiti.html")
            print(" ▶ Executando Wapiti...")
            executar_wapiti(url, saida_html)
            resultado += f"  ✅ Wapiti: {saida_html}\n"
        except Exception as e:
            resultado += f"  ❌ Wapiti falhou: {e}\n"

        try:
            nuclei_saida = f"nuclei_{bucket_url.replace('.', '_')}.txt"
            print(" ▶ Executando Nuclei...")
            executar_nuclei(url)
            resultado += f"  ✅ Nuclei: {nuclei_saida}\n"
        except Exception as e:
            resultado += f"  ❌ Nuclei falhou: {e}\n"

        return resultado

    def _salvar_relatorio(self, linhas, caminho_saida):
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            for linha in linhas:
                f.write(linha + "\n")
        print(f"\n📁 Relatório final salvo em: {caminho_saida}")

    def analisar_todos(self):
        for versao in sorted(os.listdir(self.catalogado_dir)):
            if versao.lower().startswith("v_"):
                resultado_path = os.path.join(
                    self.catalogado_dir,
                    versao,
                    f"Resultado_AnaliseV{versao[2:]}",
                    "buckets.txt"
                )
                if os.path.exists(resultado_path):
                    print(f"\n📄 Processando: {resultado_path}")
                    buckets = self._ler_buckets_txt(resultado_path)
                    for bucket_url, provedor in buckets:
                        resumo = self._rodar_analises_vulnerabilidade(bucket_url)
                        self.relatorio_final.append(resumo)
                else:
                    print(f"⚠️ Arquivo não encontrado: {resultado_path}")

        # Salvar relatório final
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_saida = os.path.join(self.base_dir, f"Relatorio_Wapiti_Nuclei_{timestamp}.txt")
        self._salvar_relatorio(self.relatorio_final, caminho_saida)
