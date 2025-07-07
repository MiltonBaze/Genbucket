class FerramentasAPI:
    def __init__(self, config: dict):
        self.config = config

    def executar_nessus(self, url: str):
        print(f"  [NESSUS] → Iniciando scan: {url}")
        try:
            token = autenticar_nessus()
            scan_id = criar_scan_nessus(token, url)
            sucesso = iniciar_scan_nessus(scan_id, token)
            print("  ✅ Nessus iniciado com sucesso" if sucesso else "  ❌ Falha ao iniciar scan")
        except Exception as e:
            print(f"  ❌ Nessus erro: {e}")

    def executar_qualys(self, url: str):
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
                f"{self.config['qualys']['host']}/qps/rest/3.0/launch/was/wasscan",
                auth=(self.config['qualys']['username'], self.config['qualys']['password']),
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
