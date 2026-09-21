# -*- coding: utf-8 -*-
"""
CineControl - Núcleo de regras de negócio (versão simplificada para fins didáticos)
=====================================================================================

Este módulo implementa, em memória (sem banco de dados real), as regras de
negócio mínimas do sistema CineControl descritas no Documento de Visão e nas
Histórias de Usuário do projeto:

    - HU01: Realizar Login
    - HU02: Gerenciar Filmes
    - HU03: Gerenciar Salas
    - HU04: Gerenciar Sessões
    - HU05: Consultar Programação
    - HU06: Realizar Reserva
    - HU07: Consultar Reservas
    - HU08: Cancelar Reserva

O código foi propositalmente mantido simples (sem persistência real em banco
de dados, sem hashing de senha, sem framework de ORM) para que o foco do
trabalho permaneça na disciplina de Teste de Software.

IMPORTANTE - BUGS PROPOSITAIS
------------------------------
Para permitir a demonstração prática de técnicas de verificação e validação
(testes unitários, de API e E2E), este módulo contém, DE FORMA PROPOSITAL,
4 defeitos de implementação. Cada um está marcado com o comentário
"# BUG PROPOSITAL". Eles estão descritos e evidenciados no Relatório Final
(seção "Execução e Evidências dos Testes").
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# "Banco de dados" em memória
# ---------------------------------------------------------------------------

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str  # "admin" ou "cliente"


@dataclass
class Filme:
    id: int
    titulo: str
    genero: str
    duracao: int
    classificacao: str
    situacao: str = "Ativo"


@dataclass
class Sala:
    id: int
    nome: str
    capacidade: int
    situacao: str = "Ativa"


@dataclass
class Sessao:
    id: int
    filme_id: int
    sala_id: int
    data: str
    horario: str
    ingressos_disponiveis: int


@dataclass
class Reserva:
    id: int
    cliente_id: int
    sessao_id: int
    quantidade: int
    situacao: str = "Confirmada"


class CineControlDB:
    """Armazenamento em memória que representa o 'banco de dados' do sistema."""

    def __init__(self):
        self.usuarios: Dict[int, Usuario] = {}
        self.filmes: Dict[int, Filme] = {}
        self.salas: Dict[int, Sala] = {}
        self.sessoes: Dict[int, Sessao] = {}
        self.reservas: Dict[int, Reserva] = {}
        self._next_id = {"usuario": 1, "filme": 1, "sala": 1, "sessao": 1, "reserva": 1}
        self._seed()

    def _new_id(self, entidade: str) -> int:
        novo_id = self._next_id[entidade]
        self._next_id[entidade] += 1
        return novo_id

    def _seed(self):
        """Popula dados mínimos para permitir uso manual (CLI) do sistema."""
        admin = Usuario(self._new_id("usuario"), "Admin CineControl",
                         "admin@cinecontrol.com", "admin123", "admin")
        cliente = Usuario(self._new_id("usuario"), "Cliente Teste",
                           "cliente@cinecontrol.com", "cliente123", "cliente")
        self.usuarios[admin.id] = admin
        self.usuarios[cliente.id] = cliente


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class ErroValidacao(Exception):
    """Erro de regra de negócio / validação de dados."""


# ---------------------------------------------------------------------------
# HU01 - Autenticação (RF01, RF02 / RN01, RN02)
# ---------------------------------------------------------------------------

def autenticar(db: CineControlDB, email: str, senha: str) -> Usuario:
    """Valida credenciais e retorna o usuário autenticado (CA1-CA7)."""
    if not email or not senha:
        raise ErroValidacao("Preencha e-mail e senha.")

    for usuario in db.usuarios.values():
        # BUG PROPOSITAL Nº 1: a comparação do e-mail é feita ignorando
        # maiúsculas/minúsculas apenas do lado armazenado, mas a senha é
        # comparada de forma correta. Isso não seria grave isoladamente,
        # porém o efeito colateral é que a validação abaixo aceita a senha
        # também sem diferenciar maiúsculas de minúsculas, o que viola a
        # regra RN01 (a senha deveria ser sensível a caixa).
        if usuario.email.lower() == email.lower() and usuario.senha.lower() == senha.lower():
            return usuario

    raise ErroValidacao("E-mail ou senha inválidos.")


# ---------------------------------------------------------------------------
# HU02 - Gerenciar Filmes (RF03-RF06 / RN03, RN10, RN12)
# ---------------------------------------------------------------------------

def cadastrar_filme(db: CineControlDB, titulo: str, genero: str, duracao: int,
                     classificacao: str = "") -> Filme:
    if not titulo or not titulo.strip():
        raise ErroValidacao("O campo Título é obrigatório.")
    if duracao is None or duracao <= 0:
        raise ErroValidacao("A duração deve ser maior que zero.")

    filme = Filme(db._new_id("filme"), titulo.strip(), genero, duracao, classificacao)
    db.filmes[filme.id] = filme
    return filme


def listar_filmes(db: CineControlDB) -> List[Filme]:
    return list(db.filmes.values())


def alterar_filme(db: CineControlDB, filme_id: int, **dados) -> Filme:
    filme = db.filmes.get(filme_id)
    if not filme:
        raise ErroValidacao("Filme não encontrado.")
    for campo, valor in dados.items():
        if hasattr(filme, campo) and valor is not None:
            setattr(filme, campo, valor)
    return filme


def excluir_filme(db: CineControlDB, filme_id: int) -> None:
    filme = db.filmes.get(filme_id)
    if not filme:
        raise ErroValidacao("Filme não encontrado.")

    # BUG PROPOSITAL Nº 2: a regra de negócio RN10 exige que a exclusão seja
    # impedida quando existirem sessões vinculadas ao filme (CA6/CA7 da
    # HU02). A verificação abaixo foi OMITIDA propositalmente: o sistema
    # permite excluir o filme mesmo havendo sessões associadas, deixando
    # sessões "órfãs" no sistema.
    del db.filmes[filme_id]


# ---------------------------------------------------------------------------
# HU03 - Gerenciar Salas (RF07-RF10 / RN04, RN10)
# ---------------------------------------------------------------------------

def cadastrar_sala(db: CineControlDB, nome: str, capacidade: int) -> Sala:
    if not nome or not nome.strip():
        raise ErroValidacao("O campo Nome/Número é obrigatório.")
    if capacidade is None or capacidade <= 0:
        raise ErroValidacao("A capacidade deve ser maior que zero.")

    sala = Sala(db._new_id("sala"), nome.strip(), capacidade)
    db.salas[sala.id] = sala
    return sala


def listar_salas(db: CineControlDB) -> List[Sala]:
    return list(db.salas.values())


def excluir_sala(db: CineControlDB, sala_id: int) -> None:
    sala = db.salas.get(sala_id)
    if not sala:
        raise ErroValidacao("Sala não encontrada.")

    tem_sessao = any(s.sala_id == sala_id for s in db.sessoes.values())
    if tem_sessao:
        raise ErroValidacao("A sala possui sessões vinculadas e não pode ser excluída.")

    del db.salas[sala_id]


# ---------------------------------------------------------------------------
# HU04 - Gerenciar Sessões (RF11-RF15 / RN05, RN06)
# ---------------------------------------------------------------------------

def cadastrar_sessao(db: CineControlDB, filme_id: int, sala_id: int,
                      data: str, horario: str) -> Sessao:
    filme = db.filmes.get(filme_id)
    sala = db.salas.get(sala_id)
    if not filme:
        raise ErroValidacao("Filme informado não existe.")
    if not sala:
        raise ErroValidacao("Sala informada não existe.")
    if not data or not horario:
        raise ErroValidacao("Data e horário são obrigatórios.")

    conflito = any(
        s.sala_id == sala_id and s.data == data and s.horario == horario
        for s in db.sessoes.values()
    )
    if conflito:
        raise ErroValidacao("Já existe uma sessão cadastrada nesta sala, data e horário.")

    sessao = Sessao(db._new_id("sessao"), filme_id, sala_id, data, horario,
                     ingressos_disponiveis=sala.capacidade)
    db.sessoes[sessao.id] = sessao
    return sessao


def listar_sessoes(db: CineControlDB) -> List[Sessao]:
    return list(db.sessoes.values())


def excluir_sessao(db: CineControlDB, sessao_id: int) -> None:
    sessao = db.sessoes.get(sessao_id)
    if not sessao:
        raise ErroValidacao("Sessão não encontrada.")
    tem_reserva = any(r.sessao_id == sessao_id and r.situacao == "Confirmada"
                       for r in db.reservas.values())
    if tem_reserva:
        raise ErroValidacao("A sessão possui reservas vinculadas e não pode ser excluída.")
    del db.sessoes[sessao_id]


# ---------------------------------------------------------------------------
# HU06 - Realizar Reserva (RF18, RF19 / RN07, RN08)
# ---------------------------------------------------------------------------

def realizar_reserva(db: CineControlDB, cliente_id: int, sessao_id: int,
                      quantidade: int) -> Reserva:
    cliente = db.usuarios.get(cliente_id)
    sessao = db.sessoes.get(sessao_id)
    if not cliente:
        raise ErroValidacao("Cliente não encontrado.")
    if not sessao:
        raise ErroValidacao("Sessão não encontrada.")

    # BUG PROPOSITAL Nº 3: o critério de aceitação CA2 da HU06 exige que a
    # quantidade seja MAIOR QUE ZERO. O código abaixo usa o operador errado
    # (">= 0" em vez de "> 0"), permitindo reservas com quantidade 0 (uma
    # reserva "vazia"), o que viola a regra RN07.
    if quantidade is None or quantidade >= 0 and quantidade == 0:
        pass  # quantidade == 0 indevidamente aceita
    elif quantidade is None or quantidade < 0:
        raise ErroValidacao("A quantidade deve ser maior que zero.")

    if quantidade > sessao.ingressos_disponiveis:
        raise ErroValidacao(
            f"Não há ingressos suficientes. Disponível: {sessao.ingressos_disponiveis}."
        )

    reserva = Reserva(db._new_id("reserva"), cliente_id, sessao_id, quantidade)
    db.reservas[reserva.id] = reserva
    sessao.ingressos_disponiveis -= quantidade
    return reserva


def listar_reservas_cliente(db: CineControlDB, cliente_id: int) -> List[Reserva]:
    return [r for r in db.reservas.values() if r.cliente_id == cliente_id]


def cancelar_reserva(db: CineControlDB, cliente_id: int, reserva_id: int) -> Reserva:
    reserva = db.reservas.get(reserva_id)
    if not reserva:
        raise ErroValidacao("Reserva não encontrada.")
    if reserva.cliente_id != cliente_id:
        raise ErroValidacao("Você não tem permissão para cancelar esta reserva.")
    if reserva.situacao == "Cancelada":
        raise ErroValidacao("Reserva já está cancelada.")

    sessao = db.sessoes.get(reserva.sessao_id)
    reserva.situacao = "Cancelada"

    # BUG PROPOSITAL Nº 4: a HU08 (CA3) exige que, ao cancelar, a quantidade
    # de ingressos da reserva seja DEVOLVIDA à disponibilidade da sessão.
    # Essa devolução foi omitida propositalmente: a reserva é marcada como
    # cancelada, mas 'sessao.ingressos_disponiveis' não é atualizado,
    # violando a integridade descrita em RN11.
    # (linha que deveria existir e foi propositalmente removida:)
    # if sessao:
    #     sessao.ingressos_disponiveis += reserva.quantidade

    return reserva
