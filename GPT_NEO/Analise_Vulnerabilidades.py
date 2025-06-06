import os
import re
from datetime import datetime
from Ferramentas_Vuln import executar_wapiti, executar_nuclei

RELATORIO_DIR = os.path.join("GPT_NEO", "Catalogados", "relatorios")
os.makedirs(RELATORIO_DIR, exist_ok=True)
base_dir = os.path.dirname(os.path.abspath(__file__))

#os.makedirs(os.path.join("GPT_NEO\Catalogados", "relatorios"), exist_ok=True)
#base_dir = os.path.dirname(os.path.abspath(__file__))

def ler_buckets_txt(caminho_arquivo):
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

def rodar_analises_vulnerabilidade(bucket_url):
    url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
    print(f"\n🔍 Analisando: {url}")
    resultado = f" Bucket: {bucket_url}\n"

    try:
        nome_bucket = bucket_url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
        saida_html = os.path.join("GPT_NEO\Catalogados", "relatorios", f"{nome_bucket}_wapiti.html")
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

def salvar_relatorio(relatorio_linhas, saida_path):
    with open(saida_path, 'w', encoding='utf-8') as f:
        for linha in relatorio_linhas:
            f.write(linha + "\n")
    print(f"\n Relatório final salvo em: {saida_path}")

# === Execução principal ===
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    catalogado_dir = os.path.join(base_dir, "Catalogados")
    relatorio_final = []

    for versao in sorted(os.listdir(catalogado_dir)):
        if versao.lower().startswith("v_"):
            resultado_path = os.path.join(
                catalogado_dir,
                versao,
                f"Resultado_AnaliseV{versao[2:]}",
                "buckets.txt"
            )
            if os.path.exists(resultado_path):
                print(f"\n Processando: {resultado_path}")
                buckets = ler_buckets_txt(resultado_path)

                for bucket_url, provedor in buckets:
                    resumo = rodar_analises_vulnerabilidade(bucket_url)
                    relatorio_final.append(resumo)
            else:
                print(f"⚠️ Arquivo não encontrado: {resultado_path}")

    # Salvar o relatório final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = os.path.join(base_dir, f"Relatorio_Wapiti_Nuclei_{timestamp}.txt")
    salvar_relatorio(relatorio_final, caminho_saida)
