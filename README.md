# LORE

**Language-based Open Research Engine**

Automated pipeline that monitors arXiv and GitHub for AI research, indexes papers with semantic embeddings, and delivers weekly synthesized digests to Notion — powered by a RAG pipeline over a local Qdrant vector store and a Groq-hosted LLM.

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-1.12-red?style=flat&logo=qdrant&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=flat&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-workflow-EA4B71?style=flat&logo=n8n&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?style=flat&logo=docker&logoColor=white)

---

## Architecture

```
┌─────────────┐    ┌─────────────┐
│    arXiv    │    │   GitHub    │
│  cs.AI      │    │  repos,     │
│  cs.LG      │    │  stars      │
│  cs.MA      │    │             │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └────────┬─────────┘
                │  fetch + embed
                ▼
        ┌───────────────┐
        │   FastAPI     │  :8000
        │  /ingest      │
        │  /search      │
        │  /synthesize  │
        │  /trends      │
        │  /digest/run  │
        └───────┬───────┘
                │  store vectors
                ▼
        ┌───────────────┐
        │    Qdrant     │  :6333
        │  all-MiniLM   │
        │  dim=384      │
        │  cosine sim   │
        └───────┬───────┘
                │  RAG retrieval
                ▼
        ┌───────────────┐
        │  LangChain +  │
        │  Groq LLM     │
        │  LLaMA 3.3    │
        │  70B          │
        └───────┬───────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│   Notion    │   │    Email    │
│  Papers     │   │  via n8n   │
│  Syntheses  │   │            │
│  Trends     │   │            │
└─────────────┘   └─────────────┘
        ▲
        │  cron trigger
┌───────────────┐
│     n8n       │  :5678
│  scheduler    │
└───────────────┘
```

---

## Quick Start

Prerequisites: Docker, Docker Compose, a Groq API key, a Notion integration token.

```bash
git clone https://github.com/<your-username>/lore
cd lore

cp .env.example .env
# fill in your keys — see the Configuration section below

docker-compose up --build
```

Once running:

| Service          | URL                             |
| ---------------- | ------------------------------- |
| FastAPI          | http://localhost:8000           |
| Swagger docs     | http://localhost:8000/docs      |
| Qdrant dashboard | http://localhost:6333/dashboard |

---

## Configuration

| Variable              | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `GROQ_API_KEY`        | Groq API key (console.groq.com)                            |
| `GROQ_MODEL`          | LLM model — default `llama-3.3-70b-versatile`              |
| `GITHUB_TOKEN`        | GitHub personal access token — optional, raises rate limit |
| `NOTION_TOKEN`        | Notion integration token (`secret_...` or `ntn_...`)       |
| `NOTION_PAPERS_DB`    | Notion Papers database ID                                  |
| `NOTION_SYNTHESES_DB` | Notion Syntheses database ID                               |
| `NOTION_TRENDS_DB`    | Notion Trends database ID                                  |
| `QDRANT_HOST`         | `qdrant` inside Docker compose, `localhost` for local dev  |
| `QDRANT_PORT`         | Default `6333`                                             |
| `EMBED_MODEL`         | Sentence Transformers model — default `all-MiniLM-L6-v2`   |

**Notion:** For each database, open it in Notion, go to `...` → Connections, and add your integration. Without this the API returns 404.

---

## Endpoints

### Ingest

Fetch papers from arXiv and repositories from GitHub, embed them, and store them in Qdrant.

```bash
curl -X POST http://localhost:8000/ingest/ \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["agentic AI", "multi-agent systems"],
    "sources": ["arxiv", "github"],
    "arxiv_categories": ["cs.AI", "cs.LG", "cs.MA"],
    "max_results": 20,
    "days": 7
  }'
```

Ingest a single document:

```bash
curl -X POST http://localhost:8000/ingest/single \
  -H "Content-Type: application/json" \
  -d '{"title": "My Paper", "abstract": "...", "url": "https://arxiv.org/abs/...", "source": "arxiv"}'
```

### Search

Semantic similarity search over the collection.

```bash
curl "http://localhost:8000/search/?q=retrieval+augmented+generation&top_k=5"

# filter by source
curl "http://localhost:8000/search/?q=agentic+AI&top_k=10&source=arxiv"
```

### Synthesize

Retrieve the most relevant documents and generate a structured synthesis via the LLM.

```bash
curl -X POST http://localhost:8000/synthesize/ \
  -H "Content-Type: application/json" \
  -d '{"query": "latest trends in agentic AI and LLM tool use", "top_k": 8}'
```

### Trends

Aggregate keyword and category counts across the entire collection.

```bash
curl "http://localhost:8000/trends/?top_n=20"
```

### Weekly Digest

Full automated pipeline: ingest → synthesize → push papers, synthesis, and trends to Notion.

```bash
curl -X POST http://localhost:8000/digest/run \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["agentic AI", "multi-agent systems"],
    "arxiv_categories": ["cs.AI", "cs.LG", "cs.MA"],
    "days": 7,
    "max_results": 50,
    "top_papers": 10,
    "top_trends": 10,
    "dry_run": false
  }'
```

Pass `"dry_run": true` to validate the pipeline without writing to Notion.

---

## n8n Integration

n8n runs separately and is not part of `docker-compose.yml`.
Connect n8n to the FastAPI Docker network first:

```bash
docker network connect ai-research-agent_default <n8n-container-name>
```

Then point HTTP Request nodes at the FastAPI service by name:

Weekly digest on a cron schedule: `POST http://fastapi:8000/digest/run`

Webhook-triggered ingest: `POST http://fastapi:8000/ingest/`

If n8n is installed locally (not Docker), use `localhost` instead.

![screenshot](docs/screenshot4.png)

---

## Project Structure

```
ai-research-agent/
├── main.py
├── routers/
│   ├── ingest.py
│   ├── search.py
│   ├── synthesize.py
│   ├── trends.py
│   └── digest.py
├── services/
│   ├── arxiv_client.py
│   ├── github_client.py
│   ├── embeddings.py
│   ├── qdrant_service.py
│   ├── llm.py
│   ├── synthesis.py
│   ├── trends.py
│   └── notion_client.py
├── utils/
│   └── retry.py
├── seed_papers.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .dockerignore
```

---

## Screenshot

![screenshot](docs/screenshot1.png)
![screenshot](docs/screenshot2.png)
![screenshot](docs/screenshot3.png)
