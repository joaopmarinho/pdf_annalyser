# ai-knowledge-base

Monorepo com backend **FastAPI** + **PostgreSQL 16 com pgvector** para upload de documentos (PDF/TXT), indexação vetorial e Q&A (RAG básico).

## Stack
- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy 2.0 async + Alembic
- PostgreSQL 16 + pgvector
- Pytest
- Ruff + Black
- Docker Compose

## Como rodar
```bash
cp .env.example .env
docker compose up --build
```

API disponível em `http://localhost:8000`.

### Health check
```bash
curl http://localhost:8000/health
```

## Endpoints
- `POST /v1/documents` - upload de PDF/TXT e indexação
- `GET /v1/documents` - lista documentos
- `GET /v1/documents/{doc_id}` - detalhe de documento
- `POST /v1/qa` - pergunta/resposta sobre um documento
- `GET /v1/questions?doc_id=...` - histórico de perguntas

## OpenAI (opcional)
Defina no `.env`:
```env
OPENAI_API_KEY=...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Sem `OPENAI_API_KEY`, o sistema usa providers **stub** locais e determinísticos (ideal para testes/dev offline).

## Exemplos de uso
### Upload
```bash
curl -X POST http://localhost:8000/v1/documents \
  -F "title=Meu Documento" \
  -F "file=@./exemplo.txt;type=text/plain"
```

### Q&A
```bash
curl -X POST http://localhost:8000/v1/qa \
  -H "Content-Type: application/json" \
  -d '{"doc_id":"<DOC_ID>","question":"Qual é o assunto do documento?","top_k":5}'
```

## Testes e qualidade
No diretório `backend/`:
```bash
pip install -e .[dev]
ruff check .
pytest -q
```

## Estrutura
```text
ai-knowledge-base/
  backend/
    app/
      api/v1/
      core/
      db/
      providers/
      services/
      utils/
      main.py
    tests/
    pyproject.toml
    Dockerfile
  docker-compose.yml
  .env.example
  README.md
  .github/workflows/ci.yml
```
