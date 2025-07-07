import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FerramentasAPI:
    def __init__(self, config: dict):
        self.nessus_config = config.get("nessus", {})
        self.qualys_config = config.get("qualys", {})

    # ===== NESSUS =====
    def autenticar_nessus(self):
        url = f"{self.nessus_config['host']}/session"
        r = requests.post(url, json={
            "username": self.nessus_config['username'],
            "password": self.nessus_config['password']
        }, verify=False)
        r.raise_for_status()
        return r.json().get("token")

    def criar_scan_nessus(self, token, target_url):
        headers = {"X-Cookie": f"token={token}"}
        data = {
            "uuid": self.nessus_config.get("scan_template_uuid"),  # 🛠 Substitua por UUID do template apropriado no seu Nessus
            "settings": {
                "name": f"Scan_{target_url}",
                "text_targets": target_url
            }
        }
        r = requests.post(
            f"{self.nessus_config['host']}/scans",
            json=data, headers=headers, verify=False
        )
        r.raise_for_status()
        return r.json()["scan"]["id"]

    def iniciar_scan_nessus(self, scan_id, token):
        headers = {"X-Cookie": f"token={token}"}
        r = requests.post(
            f"{self.nessus_config['host']}/scans/{scan_id}/launch",
            headers=headers, verify=False
        )
        r.raise_for_status()
        return r.status_code == 200

    def executar_nessus(self, url):
        print(f"  [NESSUS] → Iniciando scan: {url}")
        try:
            token = self.autenticar_nessus()
            scan_id = self.criar_scan_nessus(token, url)
            sucesso = self.iniciar_scan_nessus(scan_id, token)
            if sucesso:
                print("  ✅ Nessus iniciado com sucesso")
            else:
                print("  ❌ Falha ao iniciar o scan no Nessus")
        except Exception as e:
            print(f"  ❌ Nessus erro: {e}")

    # ===== QUALYS WAS =====
    def executar_qualys(self, url):
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
                f"{self.qualys_config['host']}/qps/rest/3.0/launch/was/wasscan",
                auth=(
                    self.qualys_config['username'],
                    self.qualys_config['password']
                ),
                headers={"Content-Type": "application/xml"},
                data=payload,
                verify=False
            )
            if r.status_code == 200:
                print("  ✅ Qualys WAS iniciado com sucesso")
            else:
                print(f"  ❌ Qualys falhou: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"  ❌ Qualys erro: {e}")
