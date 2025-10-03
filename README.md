## 🚀 BCNN Backend API

API para gerenciamento de questões alinhadas à Base Comum Nacional de Currículos (BCNN).

## 💡 O que é a aplicação

Esta API fornece endpoints para cadastrar, consultar e gerenciar questões pedagógicas (questões de prova/exercício), incluindo autenticação de usuários e logging centralizado de todos os consumos em uma coleção MongoDB (`LOGS`). A aplicação foi construída para ser leve, extensível e fácil de integrar em ferramentas de autoria e plataformas educacionais.

## ⚙️ Como iniciar

1. Instale as dependências:

```powershell
pip install -r requirements.txt
```

2. Crie um arquivo `.env` na raiz do projeto e informe as chaves necessárias (NÃO inclua valores aqui no README):

- `MONGODB_PASS`
- `DATABASE_NAME`
- `MONGODB_USER`
- `MONGODB_HOST`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Observação: mantenha esses valores seguros e fora do controle de versão. Use um ambiente virtual (venv/virtualenv) por projeto para evitar conflitos de dependências.

## ▶️ Como iniciar e acessar a aplicação

Executar em desenvolvimento (exemplo):

```powershell
# a partir da raiz do projeto
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Após iniciado consuma as rotas a partir de:

- API: http://localhost:8000

Obs.: a aplicação também pode ser iniciada diretamente com `python main.py` (executa uvicorn internamente).

## 🔐 Autenticação

- O login é feito via endpoint `/auth/login` e fornece um cookie HTTP-only chamado `access_token` que deve ser enviado em requisições subsequentes.
- Por padrão, todas as rotas (exceto `/`, `/health` e `/auth/login`) exigem autenticação via esse cookie.

## 🧭 Rotas disponíveis (método — path — parâmetros)

Nota: a lista abaixo indica os parâmetros esperados (query/path/body). Não inclui a estrutura de retorno.

- GET `/` — sem parâmetros (health básico)
- GET `/health` — sem parâmetros (health detalhado; checa conexão com MongoDB)
- Autenticação

  - POST `/auth/login` — body: `email`, `senha`
  - GET `/auth/me` — sem parâmetros (retorna usuário atual; requer cookie `access_token`)
  - POST `/auth/logout` — sem parâmetros (remove cookie de sessão)

- Questões (`/questoes`)

  - GET `/questoes/` — query: `page` (int, >=1, obrigatório), `limit` (int, default 10, 1..20), `disciplina` (opcional, enum)
  - GET `/questoes/{questao_id}` — path: `questao_id` (string)
  - POST `/questoes/adicionar` — body: objeto com dados da questão (modelo `QuestaoCreate`)

- Logs (`/logs`)

  - GET `/logs/` — query: `page` (int, default 1), `limit` (int, default 50, max 200), `origem` (opcional), `resultado` (opcional)

Consulte a documentação interativa em `/docs` para ver os modelos (schemas) e exemplos de body quando necessário.

## 🗂️ Estrutura do projeto

Estrutura principal (resumida):

```
Backend BCNN/
├─ main.py                      # Entrypoint da app (FastAPI + middleware)
├─ connection.py                # Conexão com MongoDB (pymongo + opcional Motor)
├─ requirements.txt             # Dependências do projeto
├─ README.md                    # Este arquivo
├─ config/
│  └─ settings.py               # Configurações e nomes de variáveis de ambiente
├─ routers/
│  ├─ api_routes.py             # Router raiz (include outros routers)
│  ├─ auth_routes.py            # Rotas de autenticação (login, logout, me)
│  ├─ questao_routes.py         # Rotas para CRUD/listagem de questões
│  └─ logs_routes.py            # Rotas para consulta de logs
├─ models/
│  └─ questao_model.py          # Modelos Pydantic (QuestaoCreate, QuestaoResponse, enums)
├─ services/
│  ├─ auth_service.py           # Lógica de autenticação e token JWT
│  ├─ questao_service.py        # Regras de negócio das questões
│  ├─ log_service.py            # Serviço de logging síncrono (pymongo)
│  ├─ log_service_async.py      # Serviço de logging assíncrono (Motor)
│  └─ erros.py                  # Exceções customizadas
├─ dependencies/
│  └─ auth.py                   # Dependência para obter o usuário atual
├─ scripts/                      # Scripts utilitários (ex.: geradores, imports)
└─ examples/                     # Exemplos de payloads JSON
```

## 📝 Logs

- Todos os consumos da API são registrados na coleção MongoDB indicada por `LOG_COLLECTION` (por padrão `LOGS`).
- Cada documento de log inclui, tipicamente:
  - `origem_consumo` (origem do request — p.ex. IP ou identificador de middleware)
  - `resultado_consumo` (ex.: `sucesso`, `erro`, `unauthenticated`, `preflight`)
  - `endpoint` (rota acessada)
  - `detalhes` (objeto com dados adicionais da operação — method, path, query, usuário, mensagens, exceções)
  - `timestamp`

Importante: antes de logar, avalie a necessidade de mascarar ou não inserir dados sensíveis no campo `detalhes` (PII, tokens, senhas). O projeto já evita inserir senhas em logs, mas revise conforme sua política de segurança.

## 🛠️ Tecnologias utilizadas

- Python 3.11/3.12
- FastAPI — framework web ASGI
- Uvicorn — servidor ASGI
- PyMongo — cliente MongoDB síncrono
- Motor — cliente MongoDB assíncrono (opcional, usado pelo serviço de logs assíncronos)
- Pydantic (v2) — validação e serialização de modelos
- python-dotenv — carregamento de variáveis de ambiente
- passlib / bcrypt — hashing de senhas (dependência do auth)

## ⚠️ Observações finais

- Recomenda-se rodar a aplicação em um ambiente virtual isolado (venv/virtualenv) para evitar conflitos de dependências com outras ferramentas instaladas globalmente.

Desenvolvido por Augusto Seabra
