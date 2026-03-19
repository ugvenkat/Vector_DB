# Vector Database NLP Pipeline — Setup & Usage Guide

A clean Python demo that shows the **full RAG loop** using **5 hardcoded sentences**
so you can understand every step clearly before adding real documents.

---

## How the pipeline works

```
5 hardcoded sentences  (your "document")
         │
         ▼
  Sentence Transformer  ──►  384-dim embedding vectors  (local, FREE, no API key)
         │
         ▼
  Vector Database  ──────►  store all 5 vectors
         │
  User Question  ────────►  embed question
         │                        │
         │                        ▼
         │              similarity search  ──►  top-3 matching chunks
         │                        │
         ▼                        ▼
  Claude (Anthropic)  ◄──  chunks + question  ──►  natural-language answer
```

The **same loop runs identically** for all 9 databases — only the storage and
search layer changes. Everything else (embeddings, Claude call, questions) is shared.

---

## All 9 Supported Databases

| # | Database | Group | Server? | API Key? | `pip install` |
|---|---|---|---|---|---|
| 1 | **Pinecone** | Original | ❌ Cloud | ✅ Pinecone (free) | `pinecone` |
| 2 | **Weaviate** | Original | ✅ Docker | ❌ | `weaviate-client` |
| 3 | **FAISS** | Original | ❌ In-process | ❌ | `faiss-cpu` |
| 4 | **ChromaDB** | Original | ❌ In-process | ❌ | `chromadb` |
| 5 | **Milvus** | Enterprise | ✅ Docker | ❌ | `pymilvus` |
| 6 | **Qdrant** | Enterprise | ✅ Docker | ❌ | `qdrant-client` |
| 7 | **pgvector** | Enterprise | ✅ Docker | ❌ | `psycopg2-binary pgvector` |
| 8 | **Redis** | Enterprise | ✅ Docker | ❌ | `redis` |
| 9 | **Elasticsearch** | Enterprise | ✅ Docker | ❌ | `elasticsearch` |

> **Best starting order:** `faiss` → `chromadb` → `qdrant` → `pinecone` → rest
> FAISS and ChromaDB need zero setup and are the easiest to understand first.

---

## Prerequisites

- **Python 3.10+** — https://www.python.org/downloads/
- **Docker Desktop for Windows** — https://www.docker.com/products/docker-desktop/
  *(only needed for Weaviate, Milvus, Qdrant, pgvector, Redis, Elasticsearch)*

---

## Step 1 — Create a virtual environment

Open **PowerShell** or **CMD** in the project folder:

```powershell
python -m venv venv
venv\Scripts\activate
```

---

## Step 2 — Install shared dependencies (always required)

```powershell
pip install anthropic sentence-transformers numpy
```

> The `sentence-transformers` model (`all-MiniLM-L6-v2`) downloads ~90 MB on
> first run and is then cached locally. No API key required for embeddings.

---

## Step 3 — Install the driver for your chosen DB

Install **one** of these depending on which `--db` flag you plan to use:

```powershell
# FAISS  (no server needed)
pip install faiss-cpu

# ChromaDB  (no server needed)
pip install chromadb

# Pinecone  (cloud, free tier)
pip install pinecone

# Weaviate  (Docker)
pip install weaviate-client

# Milvus  (Docker)
pip install pymilvus

# Qdrant  (Docker)
pip install qdrant-client

# pgvector  (Docker — PostgreSQL)
pip install psycopg2-binary pgvector

# Redis Stack  (Docker)
pip install redis

# Elasticsearch  (Docker)
pip install elasticsearch
```

---

## Step 4 — Get your Anthropic API key

1. Go to **https://console.anthropic.com**
2. Sign in (or create a free account)
3. Click **API Keys** in the left sidebar
4. Click **Create Key**, give it a name, and copy it

Set it in your terminal **before running the script**:

```powershell
# PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY_HERE"

# CMD
set ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

---

## Step 5 — Get your Pinecone API key *(only if using `--db pinecone`)*

1. Go to **https://www.pinecone.io** and sign up (free Starter tier)
2. In the left sidebar click **API Keys**
3. Copy your key

```powershell
# PowerShell
$env:PINECONE_API_KEY = "pcsk_YOUR_KEY_HERE"

# CMD
set PINECONE_API_KEY=pcsk_YOUR_KEY_HERE
```

> The script automatically creates a Serverless index on first run.
> This takes about **30 seconds** the very first time.

---

## Step 6 — Start the DB server (Docker-based databases only)

FAISS, ChromaDB, and Pinecone need **no server**. For all others, run the
matching Docker command below. Verify with `docker ps` afterwards.

### Weaviate
```powershell
docker run -d --name weaviate `
  -p 8080:8080 -p 50051:50051 `
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true `
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate `
  cr.weaviate.io/semitechnologies/weaviate:1.25.1
```
No API key needed. REST check: http://localhost:8080/v1

### Milvus (standalone)
```powershell
docker run -d --name milvus-standalone `
  -p 19530:19530 -p 9091:9091 `
  milvusdb/milvus:v2.4.1 standalone
```
No API key needed.

### Qdrant
```powershell
docker run -d --name qdrant `
  -p 6333:6333 qdrant/qdrant
```
No API key needed. Dashboard: http://localhost:6333/dashboard

### pgvector (PostgreSQL + vector extension)
```powershell
docker run -d --name pgvector `
  -e POSTGRES_PASSWORD=password `
  -p 5432:5432 pgvector/pgvector:pg16
```
No API key needed. Password matches the `PG_PASSWORD` config in the script.

### Redis Stack
```powershell
docker run -d --name redis-stack `
  -p 6379:6379 redis/redis-stack:latest
```
No API key needed.

### Elasticsearch
```powershell
docker run -d --name elasticsearch `
  -e "discovery.type=single-node" `
  -e "xpack.security.enabled=false" `
  -p 9200:9200 elasticsearch:8.13.0
```
No API key needed. Security is disabled for local development.

---

## Step 7 — Run the pipeline

```powershell
# No server needed — great for learning the core loop first
python vector_nlp_pipeline.py --db faiss
python vector_nlp_pipeline.py --db chromadb

# Cloud (free tier) — no Docker needed
python vector_nlp_pipeline.py --db pinecone

# Docker-based
python vector_nlp_pipeline.py --db weaviate
python vector_nlp_pipeline.py --db milvus
python vector_nlp_pipeline.py --db qdrant
python vector_nlp_pipeline.py --db pgvector
python vector_nlp_pipeline.py --db redis
python vector_nlp_pipeline.py --db elasticsearch
```

---

## Expected output (example with FAISS)

```
======================================================================
  Vector DB NLP Pipeline  —  backend: FAISS
======================================================================

📄 INPUT TEXT (5 hardcoded sentences):
  [1] Artificial intelligence is transforming industries by automating...
  [2] Vector databases store high-dimensional embeddings and retrieve...
  [3] Large language models like Claude can read retrieved text chunks...
  [4] The RAG (Retrieval-Augmented Generation) pattern combines a vector...
  [5] Sentence transformers convert raw text into dense numerical vectors...

🔢 Loading embedding model 'all-MiniLM-L6-v2' (local, free) …
   ✓  5 vectors  ×  384 dimensions

──────────────────────────────────────────────────────────────────────
❓ QUESTION : What is RAG and how does it work?

[FAISS] Building in-memory index (no server needed) …

🔍 TOP-3 RETRIEVED CHUNKS:
  [1] The RAG (Retrieval-Augmented Generation) pattern combines a vector...
  [2] Vector databases store high-dimensional embeddings and retrieve...
  [3] Large language models like Claude can read retrieved text chunks...

🤖 CLAUDE'S ANSWER:
   RAG (Retrieval-Augmented Generation) works in two steps: first it
   performs a vector similarity search to find the most relevant text
   chunks, then passes those chunks to an LLM to generate a grounded,
   context-aware answer.

======================================================================
  ✅  Done — all questions answered.
======================================================================
```

---

## How to extend this to real documents

When you are ready to move beyond the 5 hardcoded sentences, replace the
`SAMPLE_TEXT` list with chunks from a real file. A simple approach:

```python
# PDF  →  pip install pdfplumber
import pdfplumber
with pdfplumber.open("my_document.pdf") as pdf:
    full_text = "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

# Excel  →  pip install pandas openpyxl
import pandas as pd
full_text = pd.read_excel("my_data.xlsx").to_string()

# Split into overlapping chunks of ~500 characters
def chunk_text(text, size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

SAMPLE_TEXT = chunk_text(full_text)
```

Feed `SAMPLE_TEXT` into the same pipeline — everything else stays the same.

---

## Configuration reference

All connection settings live at the top of `vector_nlp_pipeline.py`:

| Variable | Default | What it controls |
|---|---|---|
| `ANTHROPIC_API_KEY` | env var | Claude LLM access |
| `PINECONE_API_KEY` | env var | Pinecone cloud access |
| `PINECONE_CLOUD` | `aws` | Cloud provider for Pinecone index |
| `PINECONE_REGION` | `us-east-1` | Region for Pinecone free tier |
| `WEAVIATE_HOST/PORT` | `localhost:8080` | Local Weaviate Docker |
| `MILVUS_HOST/PORT` | `localhost:19530` | Local Milvus Docker |
| `QDRANT_HOST/PORT` | `localhost:6333` | Local Qdrant Docker |
| `PG_HOST/PORT/PASSWORD` | `localhost:5432/password` | Local pgvector Docker |
| `REDIS_HOST/PORT` | `localhost:6379` | Local Redis Stack Docker |
| `ES_HOST` | `http://localhost:9200` | Local Elasticsearch Docker |
| `EMBED_MODEL` | `all-MiniLM-L6-v2` | Local embedding model (384-dim) |
| `TOP_K` | `3` | Number of chunks to retrieve per question |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'pinecone'` | Run `pip install pinecone` inside your activated venv — each DB needs its own driver installed separately |
| `No module named 'qdrant_client'` | Run `pip install qdrant-client` — same idea, install the driver for whichever DB you are using |
| `ModuleNotFoundError` (any DB) | Run `pip install <package>` from the table in Step 3 inside your activated venv |
| Script error says "Check DB server" | This is a generic message — the real cause is shown on the line above it (e.g. missing module, wrong API key, or server not running) |
| `Connection refused` | Docker container not started — run `docker ps` to check, then run the matching `docker run` command from Step 6 |
| `AuthenticationError` (Anthropic) | Verify `ANTHROPIC_API_KEY` is set — see "Verifying environment variables" below |
| `AuthenticationError` (Pinecone) | Verify `PINECONE_API_KEY` is set — see "Verifying environment variables" below |
| Slow first run | Embedding model is downloading (~90 MB) — wait once, then it is cached locally |
| Pinecone index timeout | First-time index creation takes ~30 s — wait for the "ready" message in the output |
| ChromaDB permission error | Delete the `./chroma_data/` folder and re-run |
| `SyntaxWarning: invalid escape sequence` | Harmless warning from a comment in the docstring — does not affect execution |
| pgvector `extension not found` | Make sure you used the `pgvector/pgvector:pg16` Docker image, not plain `postgres` |

---

## Verifying environment variables

After setting an API key, always confirm it is visible to Python before running the script.

```powershell
# Check Anthropic key
echo $env:ANTHROPIC_API_KEY

# Check Pinecone key
echo $env:PINECONE_API_KEY
```

You should see your key printed back. If the output is **blank**, the variable is not set — run the `$env:` command again.

> **Important:** environment variables set with `$env:` only last for the current
> PowerShell session. Close the window and they are gone. To make them permanent:

```powershell
# Save permanently to your Windows user profile (run once per key)
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-YOUR_KEY_HERE", "User")
[System.Environment]::SetEnvironmentVariable("PINECONE_API_KEY",  "pcsk_YOUR_KEY_HERE",   "User")
```

```powershell
# Verify the permanently saved values
[System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
[System.Environment]::GetEnvironmentVariable("PINECONE_API_KEY",  "User")
```

After running the permanent save commands, **open a new PowerShell window** — the
keys will be available automatically in every session from that point on.
