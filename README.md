# CineControl — Código de Apoio ao Trabalho de Teste de Software

Implementação simplificada do sistema **CineControl** (gerenciamento de
filmes, salas, sessões e reservas de um cinema), criada apenas para servir de
base à aplicação de **testes unitários, de API e E2E**, conforme o roteiro do
trabalho final da disciplina.

> Não há banco de dados real (os dados ficam em memória, no processo). Isso é
> proposital: o foco do trabalho é teste de software, não persistência.
> O sistema contém **4 bugs propositais**, documentados em `cinecontrol/core.py`
> (procure por `BUG PROPOSITAL`) e detalhados no relatório final entregue em
> Word, na seção "Execução e Evidências dos Testes".

## Estrutura do projeto

```
cinecontrol/
├── cinecontrol/
│   ├── core.py     # Regras de negócio (login, filmes, salas, sessões, reservas)
│   ├── api.py      # API REST (Flask) que expõe as regras de core.py
│   └── cli.py      # Interface de linha de comando (frontend simples)
├── tests/
│   ├── test_unit.py   # Testes unitários (unittest)
│   ├── test_api.py    # Testes de API (unittest + Flask test client)
│   └── test_e2e.py    # Teste E2E simulando o fluxo completo do cliente
├── requirements.txt
└── README.md
```

## Como executar

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Rodar a API

```bash
python3 -m cinecontrol.api
# API disponível em http://localhost:5000
```

### Rodar a interface de linha de comando (CLI)

```bash
python3 -m cinecontrol.cli
```
Usuários de teste já cadastrados:
- Administrador: `admin@cinecontrol.com` / `admin123`
- Cliente: `cliente@cinecontrol.com` / `cliente123`

### Rodar todos os testes (unitários + API + E2E)

Nenhuma dependência externa de teste é necessária — os testes usam apenas a
biblioteca padrão `unittest`:

```bash
python3 -m unittest discover -v tests
```

Resultado esperado: **25 testes executados, 5 falhas** — as falhas são
**esperadas e propositais**, evidenciando os 4 bugs inseridos no código (um
dos bugs é coberto tanto por um teste unitário quanto pelo teste E2E, daí as
5 falhas para 4 defeitos). O detalhamento de cada falha está no relatório
final em Word.

## Frameworks utilizados

| Tipo de teste | Framework |
|---|---|
| Unitário | `unittest` (biblioteca padrão do Python) |
| API | `unittest` + `Flask` test client |
| E2E | `unittest` + `Flask` test client (simula a jornada do usuário ponta a ponta através da API) |
