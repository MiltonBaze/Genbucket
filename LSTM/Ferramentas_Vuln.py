import subprocess
import os

RELATORIO_BASE = os.path.join("LSTM\Catalogados", "relatorios")
NUCLEI_PATH = r"C:\Ferramentas\Nuclei\nuclei.exe"  # Ajuste se necessário
WAPITI_EXE = r"C:\Ferramentas\Wapiti\wapiti.exe"  # Ajuste para o caminho real

def executar_wapiti(url, saida_html=None):
    os.makedirs(RELATORIO_BASE, exist_ok=True)
    nome_bucket = url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")

    if saida_html is None:
        saida_html = os.path.join(RELATORIO_BASE, f"{nome_bucket}_wapiti.html")

    print(f"  [WAPITI + NIKTO] → Salvando relatório em: {saida_html}")

    try:
        subprocess.run([
            WAPITI_EXE, "-u", url,
            "-m", "nikto",
            "-f", "html",
            "-o", saida_html
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Erro ao executar Wapiti com Nikto: {e}")

def executar_nuclei(url):
    os.makedirs(RELATORIO_BASE, exist_ok=True)
    nome_bucket = url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
    saida_txt = os.path.join(RELATORIO_BASE, f"{nome_bucket}_nuclei.txt")

    print(f"  [NUCLEI] → Salvando relatório em: {saida_txt}")

    try:
        subprocess.run([
            NUCLEI_PATH, "-u", url, "-o", saida_txt
        ], check=True)
    except FileNotFoundError:
        print("  ❌ Nuclei não encontrado! Verifique o caminho no NUCLEI_PATH.")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Erro ao executar Nuclei: {e}")
