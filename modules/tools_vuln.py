import os
import subprocess

def run_wapiti(url, saida_html, wapiti_path, timeout=300):
    wapiti_path = os.path.abspath(wapiti_path)
    os.makedirs(os.path.dirname(saida_html), exist_ok=True)
    print(f"  [WAPITI] → run: {wapiti_path}")
    print(f"  [WAPITI] → Salvando relatório em: {saida_html}")

    try:
        subprocess.run([
            wapiti_path, "-u", url,
            "-m", "nikto",
            "-f", "html",
            "-o", saida_html
        ], check=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"[WAPITI] Erro na execução: {e}")
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"[WAPITI] Timeout excedido para {url}")

def run_nuclei(url, relatorio_dir, nuclei_path, timeout=300):
    nuclei_path = os.path.abspath(nuclei_path)
    os.makedirs(relatorio_dir, exist_ok=True)
    nome_bucket = url.replace("https://", "").replace("http://", "").replace(".", "_").replace("/", "_")
    saida_txt = os.path.join(relatorio_dir, f"{nome_bucket}_nuclei.txt")

    print(f"  [NUCLEI] → Run: {nuclei_path}")
    print(f"  [NUCLEI] → Salvando relatório em: {saida_txt}")

    try:
        subprocess.run([
            nuclei_path, "-u", url, "-o", saida_txt
        ], check=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"[NUCLEI] Erro na execução: {e}")
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"[NUCLEI] Timeout excedido para {url}")
