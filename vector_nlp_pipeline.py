"""
================================================================================
  Vector Database NLP Pipeline  —  All 9 Databases
  --------------------------------------------------
  Group A (your original 4):
    1. Pinecone        (cloud-hosted, FREE tier available)
    2. Weaviate        (local Docker  OR  cloud)
    3. FAISS           (pure in-process library, no server)
    4. ChromaDB        (pure in-process library, no server)

  Group B (enterprise additions):
    5. Milvus          (local Docker)
    6. Qdrant          (local Docker)
    7. pgvector        (local Docker — PostgreSQL + extension)
    8. Redis           (local Docker — Redis Stack)
    9. Elasticsearch   (local Docker)

  LLM        : Anthropic Claude  (claude-sonnet-4-20250514)
  Embeddings : sentence-transformers  — runs LOCALLY, completely FREE

  HOW IT WORKS (same loop for every DB):
    1. 5 hardcoded sentences  →  each is one "chunk"
    2. Every chunk  →  384-dim embedding vector  (local sentence-transformer)
    3. All vectors  →  inserted into chosen vector DB
    4. User question  →  embed  →  similarity search  →  top-3 chunks
    5. top-3 chunks + question  →  Claude  →  natural-language answer
================================================================================

┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP-BY-STEP SETUP  (Windows PowerShell / CMD)                             │
│                                                                             │
│  1) Create & activate virtual environment                                   │
│       python -m venv venv                                                   │
│       venv\Scripts\activate                                                 │
│                                                                             │
│  2) Install shared packages (always required)                               │
│       pip install anthropic sentence-transformers numpy                     │
│                                                                             │
│  3) Install driver for YOUR chosen DB  (pick ONE row only)                  │
│       --db pinecone       →  pip install pinecone                           │
│       --db weaviate       →  pip install weaviate-client                    │
│       --db faiss          →  pip install faiss-cpu                          │
│       --db chromadb       →  pip install chromadb                           │
│       --db milvus         →  pip install pymilvus                           │
│       --db qdrant         →  pip install qdrant-client                      │
│       --db pgvector       →  pip install psycopg2-binary pgvector           │
│       --db redis          →  pip install redis                              │
│       --db elasticsearch  →  pip install elasticsearch                      │
│                                                                             │
│  4) Set your Anthropic API key                                              │
│       PowerShell : $env:ANTHROPIC_API_KEY = "sk-ant-..."                   │
│       CMD        : set ANTHROPIC_API_KEY=sk-ant-...                        │
│       Get key at : https://console.anthropic.com  →  API Keys              │
│                                                                             │
│  5) Start the DB server if required  (see DB-SETUP section below)          │
│       FAISS and ChromaDB  — NO server, run in-process                      │
│       Pinecone            — NO server, cloud-hosted (free tier)             │
│       All others          — need Docker Desktop                             │
│                             https://docker.com/products/docker-desktop      │
│                                                                             │
│  6) Run the script                                                          │
│       python vector_nlp_pipeline.py --db faiss                             │
│       python vector_nlp_pipeline.py --db chromadb                          │
│       python vector_nlp_pipeline.py --db pinecone                          │
│       python vector_nlp_pipeline.py --db weaviate                          │
│       python vector_nlp_pipeline.py --db milvus                            │
│       python vector_nlp_pipeline.py --db qdrant                            │
│       python vector_nlp_pipeline.py --db pgvector                          │
│       python vector_nlp_pipeline.py --db redis                             │
│       python vector_nlp_pipeline.py --db elasticsearch                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  DB-SETUP — Server / account startup for each database                      │
│                                                                             │
│  ── FAISS ────────────────────────────────────────────────────────────────  │
│    No server needed.  In-process C++ library wrapped in Python.            │
│    pip install faiss-cpu                                                    │
│                                                                             │
│  ── ChromaDB ─────────────────────────────────────────────────────────────  │
│    No server needed.  Stores data in ./chroma_data/ automatically.         │
│    pip install chromadb                                                     │
│                                                                             │
│  ── Pinecone ─────────────────────────────────────────────────────────────  │
│    Cloud-hosted. No Docker. Free Starter tier available.                   │
│    a) Sign up at https://www.pinecone.io  (free)                           │
│    b) Go to API Keys in the left sidebar → copy your key                   │
│    c) PowerShell: $env:PINECONE_API_KEY = "pcsk_..."                       │
│    d) Script auto-creates a Serverless index on first run (~30 sec wait)   │
│                                                                             │
│  ── Weaviate ─────────────────────────────────────────────────────────────  │
│    docker run -d --name weaviate                                            │
│      -p 8080:8080 -p 50051:50051                                            │
│      -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true                       │
│      -e PERSISTENCE_DATA_PATH=/var/lib/weaviate                            │
│      cr.weaviate.io/semitechnologies/weaviate:1.25.1                       │
│    No API key needed for local anonymous mode.                             │
│                                                                             │
│  ── Milvus (standalone) ──────────────────────────────────────────────────  │
│    docker run -d --name milvus-standalone                                  │
│      -p 19530:19530 -p 9091:9091                                            │
│      milvusdb/milvus:v2.4.1 standalone                                     │
│    No API key needed.                                                       │
│                                                                             │
│  ── Qdrant ───────────────────────────────────────────────────────────────  │
│    docker run -d --name qdrant                                              │
│      -p 6333:6333 qdrant/qdrant                                             │
│    Dashboard: http://localhost:6333/dashboard                               │
│    No API key needed.                                                       │
│                                                                             │
│  ── pgvector (PostgreSQL + vector extension) ─────────────────────────────  │
│    docker run -d --name pgvector                                            │
│      -e POSTGRES_PASSWORD=password                                         │
│      -p 5432:5432 pgvector/pgvector:pg16                                   │
│    No API key needed.                                                       │
│                                                                             │
│  ── Redis Stack ──────────────────────────────────────────────────────────  │
│    docker run -d --name redis-stack                                         │
│      -p 6379:6379 redis/redis-stack:latest                                  │
│    No API key needed.                                                       │
│                                                                             │
│  ── Elasticsearch ────────────────────────────────────────────────────────  │
│    docker run -d --name elasticsearch                                       │
│      -e "discovery.type=single-node"                                       │
│      -e "xpack.security.enabled=false"                                     │
│      -p 9200:9200 elasticsearch:8.13.0                                     │
│    No API key needed for local single-node.                                │
└─────────────────────────────────────────────────────────────────────────────┘
"""

import os
import sys
import argparse
import numpy as np

from sentence_transformers import SentenceTransformer
import anthropic

# =============================================================================
# CONFIGURATION  —  update values that match your local setup
# =============================================================================

ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_KEY_HERE")

# Pinecone (cloud)
PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY",  "YOUR_PINECONE_KEY_HERE")
PINECONE_INDEX     = "nlp-demo"
PINECONE_CLOUD     = "aws"
PINECONE_REGION    = "us-east-1"

# Weaviate (local Docker)
WEAVIATE_HOST      = "localhost"
WEAVIATE_PORT      = 8080
WEAVIATE_GRPC_PORT = 50051
WEAVIATE_CLASS     = "NlpDemo"

# Milvus (local Docker)
MILVUS_HOST        = "localhost"
MILVUS_PORT        = 19530
MILVUS_COLLECTION  = "nlp_demo"

# Qdrant (local Docker)
QDRANT_HOST        = "localhost"
QDRANT_PORT        = 6333
QDRANT_COLLECTION  = "nlp_demo"

# pgvector / PostgreSQL (local Docker)
PG_HOST            = "localhost"
PG_PORT            = 5432
PG_DB              = "postgres"
PG_USER            = "postgres"
PG_PASSWORD        = "password"
PG_TABLE           = "nlp_demo"

# Redis Stack (local Docker)
REDIS_HOST         = "localhost"
REDIS_PORT         = 6379
REDIS_INDEX        = "nlp_demo"

# Elasticsearch (local Docker)
ES_HOST            = "http://localhost:9200"
ES_INDEX           = "nlp_demo"

# Embedding (shared by all DBs)
EMBED_MODEL        = "all-MiniLM-L6-v2"   # downloads ~90 MB once, then cached
EMBED_DIM          = 384
TOP_K              = 3

# =============================================================================
# HARDCODED INPUT TEXT  —  5 sentences = our entire "document"
# =============================================================================
SAMPLE_TEXT = [
    "Artificial intelligence is transforming industries by automating complex tasks and enabling smarter decision-making.",
    "Vector databases store high-dimensional embeddings and retrieve the most semantically similar results using approximate nearest-neighbor search.",
    "Large language models like Claude can read retrieved text chunks and generate accurate, context-aware answers to user questions.",
    "The RAG (Retrieval-Augmented Generation) pattern combines a vector search step with an LLM generation step for grounded responses.",
    "Sentence transformers convert raw text into dense numerical vectors that capture semantic meaning in a compact form.",
]
# Each sentence is treated as one "chunk".
# In a real pipeline you would split a long document into overlapping windows.

# =============================================================================
# DEMO QUESTIONS  —  asked against every DB run
# =============================================================================
DEMO_QUESTIONS = [
    "What is RAG and how does it work?",
    "How do vector databases find similar results?",
    "What do sentence transformers do?",
]

# =============================================================================
# SHARED HELPERS
# =============================================================================

def get_embeddings(texts: list, model: SentenceTransformer) -> list:
    """Encode a list of strings into 384-dim float vectors (runs locally)."""
    return model.encode(texts, show_progress_bar=False).tolist()


def ask_claude(question: str, context_chunks: list) -> str:
    """Pass retrieved chunks + question to Claude, return its answer."""
    client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    context = "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(context_chunks))
    prompt  = (
        "You are a helpful assistant. Use ONLY the context below to answer.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\nANSWER:"
    )
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


# =============================================================================
# ─────────────────────────────────────────────────────────────────────────────
#   GROUP A  —  YOUR ORIGINAL 4
# ─────────────────────────────────────────────────────────────────────────────
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# 1.  PINECONE  (cloud — free Starter tier, no Docker needed)
# ─────────────────────────────────────────────────────────────────────────────
def run_pinecone(chunks, embeddings, question, q_vec):
    """
    Pinecone is fully cloud-hosted.
    How to get your free API key:
      1. Sign up at https://www.pinecone.io  (free account)
      2. Left sidebar → 'API Keys' → copy the key
      3. Set env var: $env:PINECONE_API_KEY = "pcsk_..."
    The Serverless index is created automatically on first run.
    """
    from pinecone import Pinecone, ServerlessSpec

    print("\n[Pinecone] Connecting to Pinecone cloud …")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it does not exist yet (takes ~30 s the first time)
    existing_names = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX not in existing_names:
        print(f"[Pinecone] Creating Serverless index '{PINECONE_INDEX}' (first-time, ~30s) …")
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
        )
        import time
        while not pc.describe_index(PINECONE_INDEX).status["ready"]:
            print("   … waiting for index to become ready")
            time.sleep(3)

    index = pc.Index(PINECONE_INDEX)

    # Upsert: list of (id_string, vector, metadata_dict)
    index.upsert(vectors=[
        (str(i), embeddings[i], {"text": chunks[i]})
        for i in range(len(chunks))
    ])

    # Query — returns nearest neighbours with their metadata payloads
    result = index.query(vector=q_vec, top_k=TOP_K, include_metadata=True)
    return [match["metadata"]["text"] for match in result["matches"]]


# ─────────────────────────────────────────────────────────────────────────────
# 2.  WEAVIATE  (local Docker)
# ─────────────────────────────────────────────────────────────────────────────
def run_weaviate(chunks, embeddings, question, q_vec):
    """
    Weaviate is a graph-aware vector DB with a GraphQL interface.
    We supply our own pre-computed vectors (no built-in vectorizer needed).

    Docker command:
      docker run -d --name weaviate -p 8080:8080 -p 50051:50051
        -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
        -e PERSISTENCE_DATA_PATH=/var/lib/weaviate
        cr.weaviate.io/semitechnologies/weaviate:1.25.1
    No API key needed for local anonymous mode.
    """
    import weaviate
    from weaviate.classes.config import Configure, Property, DataType
    from weaviate.classes.query  import MetadataQuery

    print("\n[Weaviate] Connecting …")
    client = weaviate.connect_to_local(
        host=WEAVIATE_HOST, port=WEAVIATE_PORT, grpc_port=WEAVIATE_GRPC_PORT
    )

    # Drop and recreate collection for a clean demo run
    if client.collections.exists(WEAVIATE_CLASS):
        client.collections.delete(WEAVIATE_CLASS)

    # vectorizer = none  means we bring our own vectors
    collection = client.collections.create(
        name=WEAVIATE_CLASS,
        vectorizer_config=Configure.Vectorizer.none(),
        properties=[Property(name="text", data_type=DataType.TEXT)],
    )

    # Batch-insert objects with their pre-computed vectors
    with collection.batch.dynamic() as batch:
        for chunk, vec in zip(chunks, embeddings):
            batch.add_object(properties={"text": chunk}, vector=vec)

    # Near-vector search (cosine distance)
    results = collection.query.near_vector(
        near_vector=q_vec,
        limit=TOP_K,
        return_metadata=MetadataQuery(distance=True),
    )
    client.close()
    return [obj.properties["text"] for obj in results.objects]


# ─────────────────────────────────────────────────────────────────────────────
# 3.  FAISS  (in-process library — NO server, NO Docker, NO API key)
# ─────────────────────────────────────────────────────────────────────────────
def run_faiss(chunks, embeddings, question, q_vec):
    """
    FAISS (Facebook AI Similarity Search) is a C++ library wrapped in Python.
    It lives entirely inside your process — nothing to install or start.
    Best choice for learning the pipeline before adding a real DB server.

    Install: pip install faiss-cpu
    GPU version (needs CUDA): pip install faiss-gpu
    """
    import faiss

    print("\n[FAISS] Building in-memory index (no server needed) …")

    # FAISS requires float32 numpy arrays
    matrix = np.array(embeddings, dtype=np.float32)

    # L2-normalise so inner-product == cosine similarity
    faiss.normalize_L2(matrix)

    # IndexFlatIP = exact brute-force inner-product search
    # Fine for a handful of docs; swap for IndexIVFFlat for millions
    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(matrix)

    # Normalise question vector the same way
    q = np.array([q_vec], dtype=np.float32)
    faiss.normalize_L2(q)

    # Search: returns (distances, row-indices) arrays
    _distances, indices = index.search(q, TOP_K)
    return [chunks[i] for i in indices[0]]


# ─────────────────────────────────────────────────────────────────────────────
# 4.  CHROMADB  (in-process library — NO server, NO Docker, NO API key)
# ─────────────────────────────────────────────────────────────────────────────
def run_chromadb(chunks, embeddings, question, q_vec):
    """
    ChromaDB is the easiest DB to start with — zero config, runs in-process.
    Data is persisted to ./chroma_data/ so it survives restarts.
    Swap PersistentClient for chromadb.Client() for a purely in-memory store.

    Install: pip install chromadb
    """
    import chromadb

    print("\n[ChromaDB] Opening local persistent collection (no server needed) …")

    # PersistentClient saves data to disk; use chromadb.Client() for RAM-only
    chroma = chromadb.PersistentClient(path="./chroma_data")

    # Drop old collection so every run is a clean slate
    try:
        chroma.delete_collection("nlp_demo")
    except Exception:
        pass

    collection = chroma.create_collection(
        name="nlp_demo",
        metadata={"hnsw:space": "cosine"},   # distance metric
    )

    # Add all chunks with their pre-computed embeddings
    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
    )

    # Query by vector  →  returns list-of-lists (one per query)
    results = collection.query(query_embeddings=[q_vec], n_results=TOP_K)
    return results["documents"][0]


# =============================================================================
# ─────────────────────────────────────────────────────────────────────────────
#   GROUP B  —  ENTERPRISE ADDITIONS
# ─────────────────────────────────────────────────────────────────────────────
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# 5.  MILVUS  (local Docker)
# ─────────────────────────────────────────────────────────────────────────────
def run_milvus(chunks, embeddings, question, q_vec):
    """
    Milvus is the most popular open-source vector DB for billion-scale workloads.
    Supports GPU acceleration, Kubernetes, and many index types (HNSW, IVF, etc.)

    Docker command:
      docker run -d --name milvus-standalone
        -p 19530:19530 -p 9091:9091
        milvusdb/milvus:v2.4.1 standalone
    No API key needed.
    """
    from pymilvus import (
        connections, Collection,
        FieldSchema, CollectionSchema, DataType, utility,
    )

    print("\n[Milvus] Connecting …")
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

    if utility.has_collection(MILVUS_COLLECTION):
        utility.drop_collection(MILVUS_COLLECTION)

    # Schema: auto-id primary key  +  text varchar  +  float vector
    fields = [
        FieldSchema(name="id",        dtype=DataType.INT64,        is_primary=True, auto_id=True),
        FieldSchema(name="text",      dtype=DataType.VARCHAR,       max_length=1000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR,  dim=EMBED_DIM),
    ]
    col = Collection(MILVUS_COLLECTION, CollectionSchema(fields))

    # Insert: pass a list per field (Milvus columnar format)
    col.insert([chunks, embeddings])
    col.flush()

    # Build HNSW index on the vector field before loading
    col.create_index("embedding", {
        "index_type": "HNSW",
        "metric_type": "COSINE",
        "params": {"M": 8, "efConstruction": 64},
    })
    col.load()

    hits = col.search(
        data=[q_vec],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"ef": 32}},
        limit=TOP_K,
        output_fields=["text"],
    )
    connections.disconnect("default")
    return [h.entity.get("text") for h in hits[0]]


# ─────────────────────────────────────────────────────────────────────────────
# 6.  QDRANT  (local Docker)
# ─────────────────────────────────────────────────────────────────────────────
def run_qdrant(chunks, embeddings, question, q_vec):
    """
    Qdrant is written in Rust — extremely fast with rich payload filtering.
    Has one of the best developer experiences among self-hosted vector DBs.

    Docker command:
      docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
    Dashboard: http://localhost:6333/dashboard
    No API key needed.
    """
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

    print("\n[Qdrant] Connecting …")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    client.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

    # Each point: integer id + vector + JSON payload
    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            PointStruct(id=i, vector=embeddings[i], payload={"text": chunks[i]})
            for i in range(len(chunks))
        ],
    )

    hits = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=q_vec,
        limit=TOP_K,
    )
    return [h.payload["text"] for h in hits]


# ─────────────────────────────────────────────────────────────────────────────
# 7.  pgvector  (local Docker — PostgreSQL + pgvector extension)
# ─────────────────────────────────────────────────────────────────────────────
def run_pgvector(chunks, embeddings, question, q_vec):
    """
    pgvector adds a 'vector' column type and HNSW/IVF indexes to PostgreSQL.
    Ideal if you already run Postgres — no new infrastructure needed.

    Docker command:
      docker run -d --name pgvector
        -e POSTGRES_PASSWORD=password
        -p 5432:5432 pgvector/pgvector:pg16
    No API key needed.
    """
    import psycopg2
    from psycopg2.extras import execute_values

    print("\n[pgvector] Connecting …")
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT,
        dbname=PG_DB, user=PG_USER, password=PG_PASSWORD,
    )
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute(f"DROP TABLE IF EXISTS {PG_TABLE};")
    cur.execute(f"""
        CREATE TABLE {PG_TABLE} (
            id        SERIAL PRIMARY KEY,
            text      TEXT,
            embedding vector({EMBED_DIM})
        );
    """)

    execute_values(
        cur,
        f"INSERT INTO {PG_TABLE} (text, embedding) VALUES %s",
        [(chunks[i], embeddings[i]) for i in range(len(chunks))],
    )

    # HNSW index — vector_cosine_ops = cosine distance
    cur.execute(f"""
        CREATE INDEX ON {PG_TABLE}
        USING hnsw (embedding vector_cosine_ops);
    """)
    conn.commit()

    # <=>  is the cosine-distance operator in pgvector
    vec_str = "[" + ",".join(str(v) for v in q_vec) + "]"
    cur.execute(f"""
        SELECT text FROM {PG_TABLE}
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (vec_str, TOP_K))

    top_chunks = [row[0] for row in cur.fetchall()]
    conn.close()
    return top_chunks


# ─────────────────────────────────────────────────────────────────────────────
# 8.  REDIS  (local Docker — Redis Stack with RediSearch module)
# ─────────────────────────────────────────────────────────────────────────────
def run_redis(chunks, embeddings, question, q_vec):
    """
    Redis Stack bundles RediSearch which adds HNSW vector indexing.
    Best for sub-millisecond latency on moderate-sized datasets.

    Docker command:
      docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
    No API key needed.
    """
    import redis as redis_lib
    from redis.commands.search.field           import TextField, VectorField
    from redis.commands.search.indexDefinition import IndexDefinition, IndexType
    from redis.commands.search.query           import Query

    print("\n[Redis] Connecting …")
    r = redis_lib.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

    try:
        r.ft(REDIS_INDEX).dropindex(delete_documents=True)
    except Exception:
        pass

    # Schema: plain text field + HNSW float32 vector field
    schema = (
        TextField("text"),
        VectorField(
            "embedding", "HNSW",
            {"TYPE": "FLOAT32", "DIM": EMBED_DIM, "DISTANCE_METRIC": "COSINE"},
        ),
    )
    r.ft(REDIS_INDEX).create_index(
        schema,
        definition=IndexDefinition(
            prefix=[f"{REDIS_INDEX}:"], index_type=IndexType.HASH
        ),
    )

    # Store each chunk as a Redis Hash (key → field → value mapping)
    for i, (chunk, vec) in enumerate(zip(chunks, embeddings)):
        r.hset(f"{REDIS_INDEX}:{i}", mapping={
            "text":      chunk,
            "embedding": np.array(vec, dtype=np.float32).tobytes(),
        })

    # RediSearch KNN query syntax
    q_bytes = np.array(q_vec, dtype=np.float32).tobytes()
    query = (
        Query(f"*=>[KNN {TOP_K} @embedding $vec AS score]")
        .sort_by("score")
        .return_fields("text", "score")
        .dialect(2)
    )
    results = r.ft(REDIS_INDEX).search(query, query_params={"vec": q_bytes})
    return [doc.text for doc in results.docs]


# ─────────────────────────────────────────────────────────────────────────────
# 9.  ELASTICSEARCH  (local Docker)
# ─────────────────────────────────────────────────────────────────────────────
def run_elasticsearch(chunks, embeddings, question, q_vec):
    """
    Elasticsearch 8+ supports dense_vector fields with built-in HNSW indexing.
    Perfect if you already use ES for text search or log analytics.

    Docker command:
      docker run -d --name elasticsearch
        -e "discovery.type=single-node"
        -e "xpack.security.enabled=false"
        -p 9200:9200 elasticsearch:8.13.0
    No API key needed for local single-node with security disabled.
    """
    from elasticsearch import Elasticsearch, helpers

    print("\n[Elasticsearch] Connecting …")
    es = Elasticsearch(ES_HOST)

    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)

    es.indices.create(index=ES_INDEX, body={
        "mappings": {
            "properties": {
                "text":      {"type": "text"},
                "embedding": {
                    "type":       "dense_vector",
                    "dims":       EMBED_DIM,
                    "index":      True,
                    "similarity": "cosine",
                },
            }
        }
    })

    helpers.bulk(es, [
        {"_index": ES_INDEX, "_id": i,
         "_source": {"text": chunks[i], "embedding": embeddings[i]}}
        for i in range(len(chunks))
    ])
    es.indices.refresh(index=ES_INDEX)

    resp = es.search(index=ES_INDEX, body={
        "knn": {
            "field":          "embedding",
            "query_vector":   q_vec,
            "k":              TOP_K,
            "num_candidates": 10,
        },
        "_source": ["text"],
    })
    return [hit["_source"]["text"] for hit in resp["hits"]["hits"]]


# =============================================================================
# DB REGISTRY  —  maps --db CLI flag to its runner function
# =============================================================================
DB_RUNNERS = {
    # ── Group A: your original 4 ──────────────────────────────────────────────
    "pinecone":       run_pinecone,       # cloud, free tier
    "weaviate":       run_weaviate,       # local Docker
    "faiss":          run_faiss,          # in-process, no server
    "chromadb":       run_chromadb,       # in-process, no server
    # ── Group B: enterprise additions ────────────────────────────────────────
    "milvus":         run_milvus,         # local Docker
    "qdrant":         run_qdrant,         # local Docker
    "pgvector":       run_pgvector,       # local Docker (PostgreSQL)
    "redis":          run_redis,          # local Docker (Redis Stack)
    "elasticsearch":  run_elasticsearch,  # local Docker
}


# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Vector DB NLP Pipeline — 9 backends",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--db",
        choices=list(DB_RUNNERS.keys()),
        required=True,
        metavar="DB",
        help=(
            "Backend to use:\n"
            "  No server : faiss, chromadb\n"
            "  Cloud     : pinecone  (free tier)\n"
            "  Docker    : weaviate, milvus, qdrant, pgvector, redis, elasticsearch"
        ),
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"  Vector DB NLP Pipeline  —  backend: {args.db.upper()}")
    print("=" * 70)

    # ── Step 1: Print hardcoded input ─────────────────────────────────────────
    print("\n📄 INPUT TEXT (5 hardcoded sentences):")
    for i, s in enumerate(SAMPLE_TEXT, 1):
        print(f"  [{i}] {s}")

    # ── Step 2: Embed all chunks locally (no API key required) ────────────────
    print(f"\n🔢 Loading embedding model '{EMBED_MODEL}' (local, free) …")
    model      = SentenceTransformer(EMBED_MODEL)
    embeddings = get_embeddings(SAMPLE_TEXT, model)
    print(f"   ✓  {len(embeddings)} vectors  ×  {len(embeddings[0])} dimensions")

    # ── Step 3: For each demo question — store → search → answer ──────────────
    runner = DB_RUNNERS[args.db]

    for question in DEMO_QUESTIONS:
        print("\n" + "─" * 70)
        print(f"❓ QUESTION : {question}")

        q_vec = get_embeddings([question], model)[0]

        try:
            top_chunks = runner(SAMPLE_TEXT, embeddings, question, q_vec)
        except Exception as exc:
            print(f"\n⚠️  DB error: {exc}")
            print("   Check that the DB server is running (see setup notes at the top).")
            sys.exit(1)

        print(f"\n🔍 TOP-{TOP_K} RETRIEVED CHUNKS:")
        for i, chunk in enumerate(top_chunks, 1):
            print(f"  [{i}] {chunk}")

        print("\n🤖 CLAUDE'S ANSWER:")
        answer = ask_claude(question, top_chunks)
        print(f"   {answer}")

    print("\n" + "=" * 70)
    print("  ✅  Done — all questions answered.")
    print("=" * 70)


if __name__ == "__main__":
    main()
