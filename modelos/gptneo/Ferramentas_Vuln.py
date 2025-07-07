import os
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
#TOOLS_DIR = os.path.join(BASE_DIR, "tools")
RELATORIO_DIR = os.path.join(BASE_DIR, "Catalogados", "relatorios")

NUCLEI_PATH = r"C:\Ferramentas\Nuclei\nuclei.exe"  # Ajuste se necessário
WAPITI_EXE = r"C:\Ferramentas\Wapiti\wapiti.exe"  # Ajuste para o caminho real

def executar_nuclei(url):
    os.makedirs(RELATORIO_DIR, exist_ok=True)
    nome = url.replace("https://", "").replace("http://", "").replace("/", "_")
    out_txt = os.path.join(RELATORIO_DIR, f"{nome}_nuclei.txt")

    print(f"\n▶ [NUCLEI] → {url}")
    try:
        subprocess.run([NUCLEI_EXEC, "-u", url, "-o", out_txt], check=True)
        print(f"✅ Relatório Nuclei salvo em: {out_txt}")
    except FileNotFoundError:
        print("❌ Nuclei não encontrado. Verifique o caminho.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Nuclei: {e}")

def executar_wapiti(url, saida_html=None):
    os.makedirs(RELATORIO_DIR, exist_ok=True)
    nome = url.replace("https://", "").replace("http://", "").replace("/", "_")
    saida_html = saida_html or os.path.join(RELATORIO_DIR, f"{nome}_wapiti.html")

    print(f"\n▶ [WAPITI] → {url}")
    try:
        subprocess.run([
            WAPITI_EXEC,
            "-u", url,
            "-m", "nikto",
            "-f", "html",
            "-o", saida_html
        ], check=True)
        print(f"✅ Relatório Wapiti salvo em: {saida_html}")
    except FileNotFoundError:
        print("❌ Wapiti não encontrado. Verifique o caminho.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Wapiti: {e}")
