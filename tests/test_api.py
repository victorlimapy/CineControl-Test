# -*- coding: utf-8 -*-
"""
Testes de API - CineControl
=============================
Framework: unittest + Flask test client (equivalente ao uso de
Postman/Supertest para fins didáticos, sem necessidade de subir um servidor
HTTP real).

Cada teste referencia o Caso de Teste (CT) correspondente do documento
"Plano de Testes e Casos de Teste".
"""
import unittest

from cinecontrol.api import create_app
from cinecontrol import core


class TestApiLogin(unittest.TestCase):
    """CT-A01, CT-A02 - POST /api/login"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_ct_a01_login_valido_retorna_200(self):
        resp = self.client.post("/api/login", json={
            "email": "admin@cinecontrol.com", "senha": "admin123"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["perfil"], "admin")

    def test_ct_a02_login_invalido_retorna_401(self):
        resp = self.client.post("/api/login", json={
            "email": "admin@cinecontrol.com", "senha": "errada"
        })
        self.assertEqual(resp.status_code, 401)


class TestApiFilmes(unittest.TestCase):
    """CT-A03, CT-A04 - /api/filmes"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_ct_a03_criar_filme_valido_retorna_201(self):
        resp = self.client.post("/api/filmes", json={
            "titulo": "Duna", "genero": "Ficção", "duracao": 155
        })
        self.assertEqual(resp.status_code, 201)

    def test_ct_a04_criar_filme_sem_titulo_retorna_400(self):
        resp = self.client.post("/api/filmes", json={
            "titulo": "", "genero": "Ficção", "duracao": 155
        })
        self.assertEqual(resp.status_code, 400)

    def test_ct_a05_listar_filmes_retorna_200(self):
        self.client.post("/api/filmes", json={
            "titulo": "Duna", "genero": "Ficção", "duracao": 155
        })
        resp = self.client.get("/api/filmes")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 1)


class TestApiSalasSessoes(unittest.TestCase):
    """CT-A06, CT-A07 - /api/salas e /api/sessoes"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_ct_a06_criar_sala_com_capacidade_invalida_retorna_400(self):
        resp = self.client.post("/api/salas", json={"nome": "Sala 1", "capacidade": -5})
        self.assertEqual(resp.status_code, 400)

    def test_ct_a07_criar_sessao_com_filme_inexistente_retorna_400(self):
        self.client.post("/api/salas", json={"nome": "Sala 1", "capacidade": 40})
        resp = self.client.post("/api/sessoes", json={
            "filme_id": 999, "sala_id": 1, "data": "2026-10-01", "horario": "20:00"
        })
        self.assertEqual(resp.status_code, 400)


class TestApiReservas(unittest.TestCase):
    """CT-A08, CT-A09 - /api/reservas"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.client.post("/api/filmes", json={"titulo": "Duna", "genero": "Ficção", "duracao": 155})
        self.client.post("/api/salas", json={"nome": "Sala 1", "capacidade": 1})
        self.client.post("/api/sessoes", json={
            "filme_id": 1, "sala_id": 1, "data": "2026-10-01", "horario": "20:00"
        })

    def test_ct_a08_reserva_valida_retorna_201(self):
        resp = self.client.post("/api/reservas", json={
            "cliente_id": 2, "sessao_id": 1, "quantidade": 1
        })
        self.assertEqual(resp.status_code, 201)

    def test_ct_a09_reserva_acima_da_capacidade_retorna_400(self):
        resp = self.client.post("/api/reservas", json={
            "cliente_id": 2, "sessao_id": 1, "quantidade": 10
        })
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
