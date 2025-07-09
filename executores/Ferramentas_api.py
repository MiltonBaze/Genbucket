import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FerramentasAPI:
    def __init__(self, config: dict):
        self.config = config
        modelo = config.get("modelo", "desconhecido")
        self.relatorios_dir = os.path.join("Resultados", modelo, "Relatorios_vulnerabilidades2")
        os.makedirs(self.relatorios_dir, exist_ok=True)

    def executar_nessus(self, url: str):
        print(f"  [NESSUS] → Iniciando scan: {url}")
        log_path = self._caminho_relatorio(url, "nessus")

        try:
            token = self.autenticar_nessus()
            scan_id = self.criar_scan_nessus(token, url)
            sucesso = self.iniciar_scan_nessus(scan_id, token)
            mensagem = "✅ Nessus iniciado com sucesso" if sucesso else "❌ Falha ao iniciar scan"
        except Exception as e:
            mensagem = f"❌ Nessus erro: {e}"

        self._salvar_log(log_path, mensagem)
        print(f"  [NESSUS] → Resultado salvo em: {log_path}")

    def executar_qualys(self, url: str):
        print(f"  [QUALYS] → Iniciando scan: {url}")
        log_path = self._caminho_relatorio(url, "qualys")

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
                mensagem = "✅ Qualys WAS iniciado com sucesso"
            else:
                mensagem = f"❌ Qualys falhou: {r.status_code} - {r.text}"
        except Exception as e:
            mensagem = f"❌ Qualys erro: {e}"

        self._salvar_log(log_path, mensagem)
        print(f"  [QUALYS] → Resultado salvo em: {log_path}")

    # ===== Métodos internos =====

    def autenticar_nessus(self):
        host = self.config["nessus"]["host"]
        username = self.config["nessus"]["username"]
        password = self.config["nessus"]["password"]

        url = f"{host}/session"
        resposta = requests.post(url, json={"username": username, "password": password}, verify=False)
        if resposta.status_code != 200:
            raise Exception(f"Falha na autenticação: {resposta.text}")
        return resposta.json()["token"]

    def criar_scan_nessus(self, token, target_url):
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

        resposta = requests.post(f"{host}/scans", json=payload, headers=headers, verify=False)
        if resposta.status_code != 200:
            raise Exception(f"Erro ao criar scan: {resposta.text}")
        return resposta.json()["scan"]["id"]

    def iniciar_scan_nessus(self, scan_id, token):
        host = self.config["nessus"]["host"]
        headers = {"X-Cookie": f"token={token}", "Content-Type": "application/json"}

        resposta = requests.post(f"{host}/scans/{scan_id}/launch", headers=headers, verify=False)
        return resposta.status_code == 200

    def _caminho_relatorio(self, url: str, ferramenta: str) -> str:
        nome = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        return os.path.join(self.relatorios_dir, f"{nome}_{ferramenta}.log")

    def _salvar_log(self, caminho: str, texto: str):
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
