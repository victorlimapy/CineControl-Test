# -*- coding: utf-8 -*-
"""
CineControl - API (backend)
============================
Camada de API REST, construída com Flask, que expõe as funcionalidades
implementadas em `core.py`. Não há banco de dados real: os dados vivem em
memória durante a execução do processo (`CineControlDB`), o que é suficiente
para os objetivos didáticos do trabalho (testes unitários, de API e E2E).
"""

from flask import Flask, jsonify, request

from . import core


def create_app(db: core.CineControlDB = None) -> Flask:
    app = Flask(__name__)
    app.config["DB"] = db if db is not None else core.CineControlDB()

    def get_db() -> core.CineControlDB:
        return app.config["DB"]

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------
    @app.post("/api/login")
    def login():
        payload = request.get_json(silent=True) or {}
        try:
            usuario = core.autenticar(get_db(), payload.get("email"), payload.get("senha"))
            return jsonify({
                "id": usuario.id, "nome": usuario.nome,
                "email": usuario.email, "perfil": usuario.perfil
            }), 200
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 401

    # ------------------------------------------------------------------
    # Filmes
    # ------------------------------------------------------------------
    @app.post("/api/filmes")
    def criar_filme():
        p = request.get_json(silent=True) or {}
        try:
            f = core.cadastrar_filme(get_db(), p.get("titulo"), p.get("genero"),
                                      p.get("duracao"), p.get("classificacao", ""))
            return jsonify(f.__dict__), 201
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 400

    @app.get("/api/filmes")
    def get_filmes():
        return jsonify([f.__dict__ for f in core.listar_filmes(get_db())]), 200

    @app.delete("/api/filmes/<int:filme_id>")
    def deletar_filme(filme_id):
        try:
            core.excluir_filme(get_db(), filme_id)
            return "", 204
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 400

    # ------------------------------------------------------------------
    # Salas
    # ------------------------------------------------------------------
    @app.post("/api/salas")
    def criar_sala():
        p = request.get_json(silent=True) or {}
        try:
            s = core.cadastrar_sala(get_db(), p.get("nome"), p.get("capacidade"))
            return jsonify(s.__dict__), 201
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 400

    @app.get("/api/salas")
    def get_salas():
        return jsonify([s.__dict__ for s in core.listar_salas(get_db())]), 200

    # ------------------------------------------------------------------
    # Sessões
    # ------------------------------------------------------------------
    @app.post("/api/sessoes")
    def criar_sessao():
        p = request.get_json(silent=True) or {}
        try:
            s = core.cadastrar_sessao(get_db(), p.get("filme_id"), p.get("sala_id"),
                                       p.get("data"), p.get("horario"))
            return jsonify(s.__dict__), 201
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 400

    @app.get("/api/sessoes")
    def get_sessoes():
        return jsonify([s.__dict__ for s in core.listar_sessoes(get_db())]), 200

    # ------------------------------------------------------------------
    # Reservas
    # ------------------------------------------------------------------
    @app.post("/api/reservas")
    def criar_reserva():
        p = request.get_json(silent=True) or {}
        try:
            r = core.realizar_reserva(get_db(), p.get("cliente_id"), p.get("sessao_id"),
                                       p.get("quantidade"))
            return jsonify(r.__dict__), 201
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 400

    @app.get("/api/clientes/<int:cliente_id>/reservas")
    def get_reservas_cliente(cliente_id):
        return jsonify([r.__dict__ for r in core.listar_reservas_cliente(get_db(), cliente_id)]), 200

    @app.post("/api/reservas/<int:reserva_id>/cancelar")
    def cancelar_reserva(reserva_id):
        p = request.get_json(silent=True) or {}
        try:
            r = core.cancelar_reserva(get_db(), p.get("cliente_id"), reserva_id)
            return jsonify(r.__dict__), 200
        except core.ErroValidacao as e:
            return jsonify({"erro": str(e)}), 400

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
