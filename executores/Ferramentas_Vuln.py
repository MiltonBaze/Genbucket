import os
import subprocess

WAPITI_EXE = r"C:\Ferramentas\Wapiti\wapiti.exe"
NUCLEI_PATH = r"C:\Ferramentas\Nuclei\nuclei.exe"

def executar_wapiti(url, saida_html):
    os.makedirs(os.path.dirname(saida_html), exist_ok=True)
    print(f"  [WAPITI] → Salvando relatório em: {saida_html}")
    subprocess.run([
        WAPITI_EXE, "-u", url,
        "-m", "nikto",
        "-f", "html",
        "-o", saida_html
    ], check=True)

def executar_nuclei(url, relatorio_dir):
    os.makedirs(relatorio_dir, exist_ok=True)
    nome_bucket = url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
    saida_txt = os.path.join(relatorio_dir, f"{nome_bucket}_nuclei.txt")
    print(f"  [NUCLEI] → Salvando relatório em: {saida_txt}")
    subprocess.run([
        NUCLEI_PATH, "-u", url, "-o", saida_txt
    ], check=True)
