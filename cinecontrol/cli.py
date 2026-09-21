# -*- coding: utf-8 -*-
"""
CineControl - Interface de linha de comando (CLI)
==================================================
Interface simples em modo texto, utilizada como "frontend" mínimo exigido
pelo roteiro do trabalho. Consome diretamente as funções de `core.py`
(nesta versão simplificada a CLI não passa pela API HTTP, mas usa as mesmas
regras de negócio que a API expõe em `api.py`).

Uso:
    python -m cinecontrol.cli
"""

from . import core


def menu():
    db = core.CineControlDB()
    usuario_logado = None

    print("=== CineControl (CLI) ===")
    print("Usuários de teste: admin@cinecontrol.com/admin123 "
          "| cliente@cinecontrol.com/cliente123")

    while True:
        if not usuario_logado:
            print("\n1) Login  0) Sair")
            opc = input("> ").strip()
            if opc == "1":
                email = input("E-mail: ").strip()
                senha = input("Senha: ").strip()
                try:
                    usuario_logado = core.autenticar(db, email, senha)
                    print(f"Bem-vindo(a), {usuario_logado.nome} ({usuario_logado.perfil})!")
                except core.ErroValidacao as e:
                    print(f"Erro: {e}")
            elif opc == "0":
                break
        else:
            print(f"\nLogado como {usuario_logado.nome} ({usuario_logado.perfil})")
            print("1) Cadastrar filme  2) Listar filmes  3) Cadastrar sala  "
                  "4) Cadastrar sessão  5) Listar sessões  6) Reservar  "
                  "7) Minhas reservas  8) Cancelar reserva  9) Logout  0) Sair")
            opc = input("> ").strip()
            try:
                if opc == "1":
                    t = input("Título: ")
                    g = input("Gênero: ")
                    d = int(input("Duração (min): "))
                    f = core.cadastrar_filme(db, t, g, d)
                    print(f"Filme cadastrado: {f}")
                elif opc == "2":
                    for f in core.listar_filmes(db):
                        print(f)
                elif opc == "3":
                    n = input("Nome/Número: ")
                    c = int(input("Capacidade: "))
                    s = core.cadastrar_sala(db, n, c)
                    print(f"Sala cadastrada: {s}")
                elif opc == "4":
                    fid = int(input("ID do filme: "))
                    sid = int(input("ID da sala: "))
                    data = input("Data (AAAA-MM-DD): ")
                    hora = input("Horário (HH:MM): ")
                    s = core.cadastrar_sessao(db, fid, sid, data, hora)
                    print(f"Sessão cadastrada: {s}")
                elif opc == "5":
                    for s in core.listar_sessoes(db):
                        print(s)
                elif opc == "6":
                    sid = int(input("ID da sessão: "))
                    qtd = int(input("Quantidade de ingressos: "))
                    r = core.realizar_reserva(db, usuario_logado.id, sid, qtd)
                    print(f"Reserva confirmada: {r}")
                elif opc == "7":
                    for r in core.listar_reservas_cliente(db, usuario_logado.id):
                        print(r)
                elif opc == "8":
                    rid = int(input("ID da reserva: "))
                    r = core.cancelar_reserva(db, usuario_logado.id, rid)
                    print(f"Reserva cancelada: {r}")
                elif opc == "9":
                    usuario_logado = None
                elif opc == "0":
                    break
            except core.ErroValidacao as e:
                print(f"Erro: {e}")
            except ValueError:
                print("Entrada inválida.")


if __name__ == "__main__":
    menu()
