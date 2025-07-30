import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ToolsAPI:
    def __init__(self, config: dict):
        self.config = config
        model = config.get("model", "unknown")
        self.reports_dir = os.path.join("Result", model, "VulnerabilityReports_v2")
        os.makedirs(self.reports_dir, exist_ok=True)

    def run_nessus(self, url: str):
        print(f"  [NESSUS] → Starting scan: {url}")
        log_path = self._get_report_path(url, "nessus")

        try:
            token = self._authenticate_nessus()
            scan_id = self._create_nessus_scan(token, url)
            success = self._launch_nessus_scan(scan_id, token)
            message = "✅ Nessus started successfully" if success else "❌ Failed to start scan"
        except Exception as e:
            message = f"❌ Nessus error: {e}"

        self._save_log(log_path, message)
        print(f"  [NESSUS] → Result saved to: {log_path}")

    def run_qualys(self, url: str):
        print(f"  [QUALYS] → Starting scan: {url}")
        log_path = self._get_report_path(url, "qualys")

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
                f"{self.config['qualys']['host']}/qps/rest/3.0/launch/was/wasscan",
                auth=(self.config['qualys']['username'], self.config['qualys']['password']),
                headers={"Content-Type": "application/xml"},
                data=payload,
                verify=False
            )
            if r.status_code == 200:
                message = "✅ Qualys WAS started successfully"
            else:
                message = f"❌ Qualys failed: {r.status_code} - {r.text}"
        except Exception as e:
            message = f"❌ Qualys error: {e}"

        self._save_log(log_path, message)
        print(f"  [QUALYS] → Result saved to: {log_path}")

    # ===== Internal methods =====

    def _authenticate_nessus(self):
        host = self.config["nessus"]["host"]
        username = self.config["nessus"]["username"]
        password = self.config["nessus"]["password"]

        url = f"{host}/session"
        response = requests.post(url, json={"username": username, "password": password}, verify=False)
        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.text}")
        return response.json()["token"]

    def _create_nessus_scan(self, token, target_url):
        host = self.config["nessus"]["host"]
        headers = {"X-Cookie": f"token={token}", "Content-Type": "application/json"}

        payload = {
            "uuid": "ab4bacd2-0c53-4c26-89c0-d3f023b25849",
            "settings": {
                "name": f"Scan_{target_url}",
                "enabled": True,
                "text_targets": target_url,
                "launch_now": False
            }
        }

        response = requests.post(f"{host}/scans", json=payload, headers=headers, verify=False)
        if response.status_code != 200:
            raise Exception(f"Failed to create scan: {response.text}")
        return response.json()["scan"]["id"]

    def _launch_nessus_scan(self, scan_id, token):
        host = self.config["nessus"]["host"]
        headers = {"X-Cookie": f"token={token}", "Content-Type": "application/json"}

        response = requests.post(f"{host}/scans/{scan_id}/launch", headers=headers, verify=False)
        return response.status_code == 200

    def _get_report_path(self, url: str, tool: str) -> str:
        name = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        return os.path.join(self.reports_dir, f"{name}_{tool}.log")

    def _save_log(self, path: str, text: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
