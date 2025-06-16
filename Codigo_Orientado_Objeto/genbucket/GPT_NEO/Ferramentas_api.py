import requests
import os
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carrega configuração de API
def carregar_config():
    caminho = os.path.join(os.path.dirname(__file__), "Ferramentas.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

config = carregar_config()

# === Nessus ===
def autenticar_nessus():
    url = f"{config['nessus']['host']}/session"
    r = requests.post(url, json={
        "username": config['nessus']['username'],
        "password": config['nessus']['password']
    }, verify=False)
    return r.json().get("token")

def criar_scan_nessus(token, url):
    headers = {"X-Cookie": f"token={token}"}
    data = {
        "uuid": "your_scan_template_uuid",  # 🔁 Substitua por UUID do template
        "settings": {
            "name": f"Scan_{url}",
            "text_targets": url
        }
    }
    r = requests.post(f"{config['nessus']['host']}/scans", json=data, headers=headers, verify=False)
    return r.json()["scan"]["id"]

def iniciar_scan_nessus(scan_id, token):
    headers = {"X-Cookie": f"token={token}"}
    r = requests.post(f"{config['nessus']['host']}/scans/{scan_id}/launch", headers=headers, verify=False)
    return r.status_code == 200

def executar_nessus(url):
    print(f"  [NESSUS] → Iniciando scan: {url}")
    try:
        token = autenticar_nessus()
        scan_id = criar_scan_nessus(token, url)
        sucesso = iniciar_scan_nessus(scan_id, token)
        print("  ✅ Nessus iniciado com sucesso" if sucesso else "  ❌ Falha ao iniciar scan")
    except Exception as e:
        print(f"  ❌ Nessus erro: {e}")

# === Qualys WAS ===
def executar_qualys(url):
    print(f"  [QUALYS] → Iniciando scan: {url}")
    payload = f"""
    <ServiceRequest>
      <data>
        <WasScan>
          <name>Scan_{url}</name>
          <type>VULNERABILITY</type>
          <target>{url}</target>
        </WasScan>
      </data>
    </ServiceRequest>
    """
    try:
        r = requests.post(
            f"{config['qualys']['host']}/qps/rest/3.0/launch/was/wasscan",
            auth=(config['qualys']['username'], config['qualys']['password']),
            headers={"Content-Type": "application/xml"},
            data=payload,
            verify=False
        )
        if r.status_code == 200:
            print("  ✅ Qualys WAS iniciado com sucesso")
        else:
            print(f"  ❌ Qualys falhou: {r.text}")
    except Exception as e:
        print(f"  ❌ Qualys erro: {e}")
