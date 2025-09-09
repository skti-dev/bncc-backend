# BCNN Backend API

API para gerenciamento de questões do BCNN (Base Comum Nacional de Currículos).

## 🚀 Como iniciar a aplicação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
MONGODB_PASS=sua_senha_mongodb
DATABASE_NAME=bcnn_database
```

### 3. Iniciar a aplicação

```bash
# Opção 1: Usando Python diretamente
python main.py

# Opção 2: Usando uvicorn (recomendado para desenvolvimento)
uvicorn main:app --reload

# Opção 3: Usando uvicorn com configurações específicas
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Acessar a aplicação

- **API**: http://localhost:8000
- **Documentação automática**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

## 📋 Rotas disponíveis

### Health Check

- **GET** `/` - Verificação básica da API
- **GET** `/health` - Verificação detalhada (inclui status do MongoDB)

### Questões

- **POST** `/questoes/adicionar` - Adiciona uma nova questão

- **GET** `/questoes/{id}` - Busca uma questão específica pelo ID

- **POST** `/questoes/adicionar` - Adiciona uma nova questão

## 📝 Exemplo de uso

### Adicionar uma questão

**Endpoint**: `POST /questoes/adicionar`

**Body**:

```json
{
  "disciplina": {
    "codigo": "MAT001",
    "nome": "Matemática"
  },
  "ano": {
    "codigo": 9,
    "descricao": "9º Ano do Ensino Fundamental"
  },
  "codigo_habilidade": "EF09MA01",
  "questao": {
    "tipo": "multipla_escolha",
    "enunciado": "Qual é o resultado da expressão 2x + 3 quando x = 5?",
    "alternativas": [
      { "letra": "A", "texto": "10" },
      { "letra": "B", "texto": "13" },
      { "letra": "C", "texto": "15" },
      { "letra": "D", "texto": "8" }
    ],
    "gabarito": "B",
    "explicacao": "Substituindo x = 5 na expressão: 2(5) + 3 = 10 + 3 = 13"
  },
  "metadados": {
    "nivel_dificuldade": "medio",
    "tempo_estimado_segundos": 120,
    "tags": ["algebra", "expressoes", "substituicao"]
  }
}
```

**Resposta**:

```json
{
  "message": "Questão adicionada com sucesso!",
  "questao_id": "674f8a1b2c3d4e5f67890abc",
  "questao": {
    "_id": "674f8a1b2c3d4e5f67890abc",
    "disciplina": {...},
    "ano": {...},
    "codigo_habilidade": "EF09MA01",
    "questao": {...},
    "metadados": {...},
    "created_at": "2024-12-03T10:30:00.000Z",
    "updated_at": "2024-12-03T10:30:00.000Z"
  }
}
```

## 🏗️ Estrutura do projeto

```
Backend BCNN/
├── .env                    # Variáveis de ambiente
├── main.py                 # Arquivo principal da aplicação
├── connection.py           # Conexão com MongoDB
├── requirements.txt        # Dependências
├── config/
│   └── settings.py        # Configurações centralizadas
├── models/
│   └── questao_model.py   # Modelos de dados
├── routers/
│   └── questao_routes.py  # Rotas da API
├── services/
│   ├── log_service.py     # Serviço de logging
│   └── questao_service.py # Lógica de negócio das questões
└── examples/
    └── questoes_adicionar.json # Exemplo de JSON para adicionar questões
```

## 📊 Logs

Todos os consumos da API são automaticamente logados na coleção `logs_api` do MongoDB, incluindo:

- Origem do consumo (IP)
- Resultado (sucesso/erro)
- Endpoint acessado
- Detalhes da operação
- Timestamp

## 🔧 Tecnologias utilizadas

- **FastAPI** - Framework web
- **MongoDB** - Banco de dados
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI
- **python-dotenv** - Gerenciamento de variáveis de ambiente
