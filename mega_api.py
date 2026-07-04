"""
mega_api.py - Cliente didatico para a API REST do Mega ERP (Senior/Mega)

Objetivo: substituir a automacao de tela (cliques + clipboard) por chamadas
HTTP diretas. Muito mais rapido, estavel e sem depender de janela aberta.

FLUXO:
  1) autenticar()  -> troca usuario/senha por um token (crachá) valido por 2h
  2) get()         -> faz qualquer consulta usando o token no cabecalho

PRE-REQUISITOS (peça ao TI / parceiro Mega):
  - TenantId da empresa
  - Usuario Mega marcado como "Usuario de APIs" + senha
  - API "Estoque [REST]" ativada para o seu tenant
  - Confirmar a URL base (Cloud = https://rest.megaerp.online)

Instale a dependencia:
  pip install requests
"""

import requests


# ============================================================
# CONFIGURACAO  (preencha com os seus dados)
# ============================================================
BASE_URL   = "https://rest.megaerp.online"   # Mega Cloud XT. On-Premise muda.
TENANT_ID  = "SEU_TENANT_ID"                 # identificador da empresa
USUARIO    = "SEU_USUARIO_API"               # usuario marcado como "Usuario de APIs"
SENHA      = "SUA_SENHA"

# ATENCAO: o caminho exato do login e do estoque voce confirma no Postman
# importando a colecao de dev.mega.com.br. Os valores abaixo sao o padrao
# mais comum, mas TROQUE pelos que aparecerem na sua colecao.
PATH_LOGIN   = "/api/Autenticacao/Autenticar"
PATH_ESTOQUE = "/api/Estoque"   # placeholder: ajuste conforme a colecao real


class MegaAPI:
    """Cliente minimo: guarda o token e injeta o cabecalho Authorization."""

    def __init__(self, base_url, tenant_id, usuario, senha):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.usuario = usuario
        self.senha = senha
        self.token = None
        # Sessao reaproveita a conexao TCP entre chamadas (mais rapido)
        self.sessao = requests.Session()

    # --------------------------------------------------------
    # PASSO 1 - Autenticar: usuario/senha -> token
    # --------------------------------------------------------
    def autenticar(self):
        url = f"{self.base_url}{PATH_LOGIN}"
        headers = {
            "tenantId": self.tenant_id,       # <-- o tenant vai no HEADER
            "Content-Type": "application/json",
        }
        body = {
            "userName": self.usuario,         # <-- usuario/senha vao no BODY (JSON)
            "password": self.senha,
        }
        resp = self.sessao.post(url, json=body, headers=headers, timeout=30)
        resp.raise_for_status()               # levanta erro se HTTP != 2xx
        dados = resp.json()

        # O nome do campo pode variar ("token", "accessToken"...). Ajuste se
        # necessario olhando o JSON de resposta no Postman.
        self.token = dados.get("token") or dados.get("accessToken")
        if not self.token:
            raise RuntimeError(f"Login sem token na resposta: {dados}")
        print("[OK] Autenticado. Token valido por ~2h.")
        return self.token

    # --------------------------------------------------------
    # PASSO 2 - Consulta autenticada (GET generico)
    # --------------------------------------------------------
    def get(self, caminho, params=None):
        if not self.token:
            self.autenticar()
        url = f"{self.base_url}{caminho}"
        headers = {
            "Authorization": f"Bearer {self.token}",  # <-- o cracha
            "tenantId": self.tenant_id,
        }
        resp = self.sessao.get(url, headers=headers, params=params, timeout=60)

        # Se o token expirou (401), reautentica uma vez e tenta de novo.
        if resp.status_code == 401:
            print("[..] Token expirado, reautenticando...")
            self.autenticar()
            headers["Authorization"] = f"Bearer {self.token}"
            resp = self.sessao.get(url, headers=headers, params=params, timeout=60)

        resp.raise_for_status()
        return resp.json()

    # --------------------------------------------------------
    # Exemplo especifico: consultar estoque/movimento de um codigo
    # --------------------------------------------------------
    def consultar_estoque(self, codigo, **filtros):
        """
        Consulta o estoque de um codigo. Os NOMES dos parametros
        (ex.: 'codigo', 'produto', 'dataInicial'...) dependem da sua
        colecao real - confira no Postman e ajuste o dicionario abaixo.
        """
        params = {"codigo": codigo}
        params.update(filtros)
        return self.get(PATH_ESTOQUE, params=params)


# ============================================================
# TESTE RAPIDO
# ============================================================
if __name__ == "__main__":
    api = MegaAPI(BASE_URL, TENANT_ID, USUARIO, SENHA)

    # 1) Autentica
    api.autenticar()

    # 2) Consulta um codigo de exemplo e imprime o JSON cru para voce
    #    ENXERGAR os campos que a API devolve (codigo, data, valor unitario...)
    try:
        resultado = api.consultar_estoque("02001")
        print("\n--- Resposta da API (JSON) ---")
        print(resultado)
    except requests.HTTPError as e:
        print(f"\n[ERRO HTTP] {e}")
        print("Verifique: URL/caminho do endpoint, TenantId, usuario de API e permissoes.")
