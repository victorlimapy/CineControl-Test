# -*- coding: utf-8 -*-
"""
Testes Unitários - CineControl
===============================
Framework: unittest (biblioteca padrão do Python).
Cobrem as funções de regra de negócio do módulo `cinecontrol.core`,
relacionadas às Histórias de Usuário HU01, HU02, HU03, HU04 e HU06.

Cada teste referencia o(s) Caso(s) de Teste (CT) correspondente(s), listados
no documento "Plano de Testes e Casos de Teste" do CineControl.
"""
import unittest

from cinecontrol import core


class TestAutenticacao(unittest.TestCase):
    """HU01 - Realizar Login (CT-U01 a CT-U03)"""

    def setUp(self):
        self.db = core.CineControlDB()

    def test_ct_u01_login_com_credenciais_validas(self):
        usuario = core.autenticar(self.db, "admin@cinecontrol.com", "admin123")
        self.assertEqual(usuario.perfil, "admin")

    def test_ct_u02_login_com_senha_incorreta_deve_falhar(self):
        with self.assertRaises(core.ErroValidacao):
            core.autenticar(self.db, "admin@cinecontrol.com", "senha_errada")

    def test_ct_u03_login_deve_ser_case_sensitive_na_senha(self):
        """
        BUG PROPOSITAL Nº 1: a senha não deveria ser aceita com caixa
        diferente da cadastrada (RN01). Este teste DEVE FALHAR na
        implementação atual, evidenciando o defeito.
        """
        with self.assertRaises(core.ErroValidacao):
            core.autenticar(self.db, "admin@cinecontrol.com", "ADMIN123")


class TestGerenciarFilmes(unittest.TestCase):
    """HU02 - Gerenciar Filmes (CT-U04 a CT-U07)"""

    def setUp(self):
        self.db = core.CineControlDB()

    def test_ct_u04_cadastrar_filme_valido(self):
        filme = core.cadastrar_filme(self.db, "Duna", "Ficção", 155)
        self.assertEqual(len(core.listar_filmes(self.db)), 1)
        self.assertEqual(filme.titulo, "Duna")

    def test_ct_u05_cadastrar_filme_sem_titulo_deve_falhar(self):
        with self.assertRaises(core.ErroValidacao):
            core.cadastrar_filme(self.db, "", "Ficção", 120)

    def test_ct_u06_cadastrar_filme_com_duracao_invalida_deve_falhar(self):
        with self.assertRaises(core.ErroValidacao):
            core.cadastrar_filme(self.db, "Filme X", "Ação", 0)

    def test_ct_u07_excluir_filme_com_sessao_vinculada_deve_ser_impedido(self):
        """
        BUG PROPOSITAL Nº 2: a exclusão de um filme com sessão vinculada
        deveria ser IMPEDIDA (RN10 / CA7-HU02). Este teste DEVE FALHAR na
        implementação atual, evidenciando o defeito.
        """
        filme = core.cadastrar_filme(self.db, "Duna", "Ficção", 155)
        sala = core.cadastrar_sala(self.db, "Sala 1", 50)
        core.cadastrar_sessao(self.db, filme.id, sala.id, "2026-10-01", "20:00")

        with self.assertRaises(core.ErroValidacao):
            core.excluir_filme(self.db, filme.id)


class TestGerenciarSalas(unittest.TestCase):
    """HU03 - Gerenciar Salas (CT-U08, CT-U09)"""

    def setUp(self):
        self.db = core.CineControlDB()

    def test_ct_u08_cadastrar_sala_valida(self):
        sala = core.cadastrar_sala(self.db, "Sala 1", 80)
        self.assertEqual(sala.capacidade, 80)

    def test_ct_u09_cadastrar_sala_com_capacidade_invalida_deve_falhar(self):
        with self.assertRaises(core.ErroValidacao):
            core.cadastrar_sala(self.db, "Sala 2", 0)


class TestGerenciarSessoes(unittest.TestCase):
    """HU04 - Gerenciar Sessões (CT-U10, CT-U11)"""

    def setUp(self):
        self.db = core.CineControlDB()
        self.filme = core.cadastrar_filme(self.db, "Duna", "Ficção", 155)
        self.sala = core.cadastrar_sala(self.db, "Sala 1", 50)

    def test_ct_u10_cadastrar_sessao_define_ingressos_pela_capacidade(self):
        sessao = core.cadastrar_sessao(self.db, self.filme.id, self.sala.id,
                                        "2026-10-01", "20:00")
        self.assertEqual(sessao.ingressos_disponiveis, 50)

    def test_ct_u11_cadastrar_sessao_com_conflito_de_horario_deve_falhar(self):
        core.cadastrar_sessao(self.db, self.filme.id, self.sala.id, "2026-10-01", "20:00")
        with self.assertRaises(core.ErroValidacao):
            core.cadastrar_sessao(self.db, self.filme.id, self.sala.id, "2026-10-01", "20:00")


class TestReservas(unittest.TestCase):
    """HU06 - Realizar Reserva / HU08 - Cancelar Reserva (CT-U12 a CT-U15)"""

    def setUp(self):
        self.db = core.CineControlDB()
        self.filme = core.cadastrar_filme(self.db, "Duna", "Ficção", 155)
        self.sala = core.cadastrar_sala(self.db, "Sala 1", 2)
        self.sessao = core.cadastrar_sessao(self.db, self.filme.id, self.sala.id,
                                             "2026-10-01", "20:00")
        self.cliente_id = 2  # cliente semeado por padrão em CineControlDB._seed

    def test_ct_u12_reserva_valida_reduz_ingressos_disponiveis(self):
        core.realizar_reserva(self.db, self.cliente_id, self.sessao.id, 2)
        sessao_atualizada = self.db.sessoes[self.sessao.id]
        self.assertEqual(sessao_atualizada.ingressos_disponiveis, 0)

    def test_ct_u13_reserva_acima_da_disponibilidade_deve_falhar(self):
        with self.assertRaises(core.ErroValidacao):
            core.realizar_reserva(self.db, self.cliente_id, self.sessao.id, 5)

    def test_ct_u14_reserva_com_quantidade_zero_deve_falhar(self):
        """
        BUG PROPOSITAL Nº 3: reservas com quantidade igual a zero deveriam
        ser rejeitadas (CA2-HU06 / RN07). Este teste DEVE FALHAR na
        implementação atual, evidenciando o defeito.
        """
        with self.assertRaises(core.ErroValidacao):
            core.realizar_reserva(self.db, self.cliente_id, self.sessao.id, 0)

    def test_ct_u15_cancelar_reserva_deve_devolver_ingressos(self):
        """
        BUG PROPOSITAL Nº 4: ao cancelar uma reserva, os ingressos deveriam
        voltar à disponibilidade da sessão (CA3-HU08 / RN11). Este teste
        DEVE FALHAR na implementação atual, evidenciando o defeito.
        """
        reserva = core.realizar_reserva(self.db, self.cliente_id, self.sessao.id, 1)
        core.cancelar_reserva(self.db, self.cliente_id, reserva.id)
        sessao_atualizada = self.db.sessoes[self.sessao.id]
        self.assertEqual(sessao_atualizada.ingressos_disponiveis, 2)


if __name__ == "__main__":
    unittest.main()
