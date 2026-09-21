# -*- coding: utf-8 -*-
"""
Teste E2E (Ponta a Ponta) - CineControl
=========================================
Framework: unittest + Flask test client, simulando a jornada completa do
usuário através da API (equivalente, em escala reduzida, ao que seria feito
com Cypress/Playwright/Selenium sobre uma interface gráfica real).

Fluxo simulado (CT-E01), conforme descrito no Documento de Visão (seção 19.3)
e na HU06:

    Login (cliente) -> Consulta de Programação -> Escolha de Sessão
    -> Realizar Reserva -> Confirmação -> Consultar Minhas Reservas
    -> Cancelar Reserva

Pré-condição: um Administrador cadastra Filme, Sala e Sessão antes do fluxo
do cliente (fluxo do administrador, HU02/HU03/HU04).
"""
import unittest

from cinecontrol.api import create_app


class TestFluxoCompletoReserva(unittest.TestCase):
    """CT-E01 - Fluxo completo: login -> consulta -> reserva -> confirmação"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_ct_e01_fluxo_completo_de_reserva_do_cliente(self):
        # 1. Administrador faz login
        resp = self.client.post("/api/login", json={
            "email": "admin@cinecontrol.com", "senha": "admin123"
        })
        self.assertEqual(resp.status_code, 200, "Login do administrador deveria funcionar")

        # 2. Administrador cadastra filme, sala e sessão
        resp = self.client.post("/api/filmes", json={
            "titulo": "Duna: Parte Dois", "genero": "Ficção", "duracao": 166
        })
        self.assertEqual(resp.status_code, 201)
        filme_id = resp.get_json()["id"]

        resp = self.client.post("/api/salas", json={"nome": "Sala 3", "capacidade": 30})
        self.assertEqual(resp.status_code, 201)
        sala_id = resp.get_json()["id"]

        resp = self.client.post("/api/sessoes", json={
            "filme_id": filme_id, "sala_id": sala_id,
            "data": "2026-10-05", "horario": "19:30"
        })
        self.assertEqual(resp.status_code, 201)
        sessao_id = resp.get_json()["id"]

        # 3. Cliente faz login
        resp = self.client.post("/api/login", json={
            "email": "cliente@cinecontrol.com", "senha": "cliente123"
        })
        self.assertEqual(resp.status_code, 200)
        cliente_id = resp.get_json()["id"]

        # 4. Cliente consulta a programação (sessões disponíveis)
        resp = self.client.get("/api/sessoes")
        self.assertEqual(resp.status_code, 200)
        sessoes_disponiveis = [s for s in resp.get_json() if s["id"] == sessao_id]
        self.assertEqual(len(sessoes_disponiveis), 1, "A sessão cadastrada deveria aparecer na programação")

        # 5. Cliente realiza a reserva de 2 ingressos
        resp = self.client.post("/api/reservas", json={
            "cliente_id": cliente_id, "sessao_id": sessao_id, "quantidade": 2
        })
        self.assertEqual(resp.status_code, 201, "A reserva deveria ser confirmada")
        reserva_id = resp.get_json()["id"]

        # 6. Cliente consulta "Minhas Reservas" e encontra a reserva feita
        resp = self.client.get(f"/api/clientes/{cliente_id}/reservas")
        self.assertEqual(resp.status_code, 200)
        reservas = resp.get_json()
        self.assertEqual(len(reservas), 1)
        self.assertEqual(reservas[0]["quantidade"], 2)

        # 7. A disponibilidade da sessão deve ter sido reduzida de 30 para 28
        resp = self.client.get("/api/sessoes")
        sessao_atual = [s for s in resp.get_json() if s["id"] == sessao_id][0]
        self.assertEqual(sessao_atual["ingressos_disponiveis"], 28)

        # 8. Cliente cancela a reserva
        resp = self.client.post(f"/api/reservas/{reserva_id}/cancelar", json={
            "cliente_id": cliente_id
        })
        self.assertEqual(resp.status_code, 200)

        # 9. Após o cancelamento, a disponibilidade deveria voltar a 30
        #    BUG PROPOSITAL Nº 4 (mesmo defeito do teste unitário CT-U15):
        #    este passo do fluxo E2E DEVE FALHAR na implementação atual.
        resp = self.client.get("/api/sessoes")
        sessao_final = [s for s in resp.get_json() if s["id"] == sessao_id][0]
        self.assertEqual(
            sessao_final["ingressos_disponiveis"], 30,
            "Ingressos deveriam ter sido devolvidos após o cancelamento (RN11)"
        )


if __name__ == "__main__":
    unittest.main()
