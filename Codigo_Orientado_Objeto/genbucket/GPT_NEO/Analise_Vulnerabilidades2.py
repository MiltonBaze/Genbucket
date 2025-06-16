import os
import re
from datetime import datetime
from Ferramentas_api import executar_nessus, executar_qualys

RELATORIO_DIR = os.path.join("GPT_NEO", "Catalogados", "relatorios")
os.makedirs(RELATORIO_DIR, exist_ok=True)
base_dir = os.path.dirname(os.path.abspath(__file__))

def ler_buckets_txt(caminho_arquivo):
    buckets = []
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            match = re.match(r'^(.*?) - provedor (\w+):$', linha.strip())
            if match:
                buckets.append((match.group(1), match.group(2)))
    return buckets

def rodar(bucket_url):
    url = f"https://{bucket_url}" if not bucket_url.startswith("http") else bucket_url
    nome = url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
    print(f"\n🔍 Analisando: {url}")
    resultado = f"📦 Bucket: {bucket_url}\n"

    try:
        print(" ▶ Nessus...")
        executar_nessus(url)
        resultado += f"  ✅ Nessus: OK\n"
    except Exception as e:
        resultado += f"  ❌ Nessus falhou: {e}\n"

    try:
        print(" ▶ Qualys WAS...")
        executar_qualys(url)
        resultado += f"  ✅ Qualys: OK\n"
    except Exception as e:
        resultado += f"  ❌ Qualys falhou: {e}\n"

    return resultado

def salvar(relatorio, saida):
    with open(saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(relatorio))
    print(f"\n Relatório salvo em: {saida}")

if __name__ == "__main__":
    relatorio_final = []
    catalogado_dir = os.path.join(base_dir, "Catalogados")

    for versao in sorted(os.listdir(catalogado_dir)):
        if versao.lower().startswith("v_"):
            path_buckets = os.path.join(
                catalogado_dir, versao,
                f"Resultado_AnaliseV{versao[2:]}",
                "buckets.txt"
            )
            if os.path.exists(path_buckets):
                print(f"\n📂 Processando: {path_buckets}")
                buckets = ler_buckets_txt(path_buckets)
                for bucket_url, _ in buckets:
                    resumo = rodar(bucket_url)
                    relatorio_final.append(resumo)
            else:
                print(f"⚠️ Arquivo não encontrado: {path_buckets}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = os.path.join(base_dir, f"relatorio_nessus_qualys_{ts}.txt")
    salvar(relatorio_final, saida)
