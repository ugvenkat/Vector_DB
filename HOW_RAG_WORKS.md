# How the RAG Pipeline Works — A Plain English Explanation

A quick guide to share with someone learning how Retrieval-Augmented Generation
(RAG) works, using our Vector DB NLP Pipeline as a concrete example.

---

## What actually happens when you run the script

When you ran `--db pinecone` and asked *"What is RAG and how does it work?"*,
here is exactly what happened step by step:

```
Your question
     │
     ▼
Sentence Transformer converts question → 384-dim vector
     │
     ▼
Pinecone searches all stored vectors for closest matches
     │
     ▼
Top-3 most similar chunks returned
  [1] The RAG pattern combines a vector search step with an LLM generation step...
  [2] Sentence transformers convert raw text into dense numerical vectors...
  [3] Large language models like Claude can read retrieved text chunks...
     │
     ▼
All 3 chunks + your question sent to Claude together
     │
     ▼
Claude synthesizes all 3 chunks into one coherent answer
```

---

## Why did Claude give such a detailed answer?

You might have expected just this one line back:

> *"The RAG (Retrieval-Augmented Generation) pattern combines a vector search
> step with an LLM generation step for grounded responses."*

But Claude actually received **all 3 retrieved chunks** as context, not just the
best one. It then **synthesized** them into a structured answer — that is where
the detailed explanation of "Vector search step" and "LLM generation step" came
from. Claude is not making things up or pulling from outside knowledge; it is
combining the meaning from all 3 chunks and writing a coherent response.

This is the core value of RAG — the LLM doesn't just echo back a chunk, it
**reasons over the retrieved context** to give a better answer than any single
chunk could on its own.

---

## The prompt that controls Claude's behaviour

Inside the script, this is the exact instruction sent to Claude:

```python
prompt = (
    "You are a helpful assistant. Use ONLY the context below to answer.\n\n"
    f"CONTEXT:\n{context}\n\n"       # <-- the 3 retrieved chunks go here
    f"QUESTION: {question}\n\n"
    "ANSWER:"
)
```

The key phrase is **"Use ONLY the context below"** — this keeps Claude grounded
to your data and prevents it from inventing answers from its general training.

---

## Two easy ways to control the output

### Option 1 — Make Claude answer more concisely

Change the prompt instruction at the top of `vector_nlp_pipeline.py`:

```python
# Original
"You are a helpful assistant. Use ONLY the context below to answer.\n\n"

# More concise version
"Answer in 1-2 sentences using ONLY the context below. Be concise.\n\n"
```

### Option 2 — Send only the single best chunk instead of top-3

Change the `TOP_K` value near the top of the script:

```python
TOP_K = 1   # default was 3
```

With `TOP_K = 1`, only the closest matching chunk is sent to Claude, so the
answer will be shorter and more focused.

---

## The three roles in a RAG pipeline

| Role | What it does | Tool used in this script |
|---|---|---|
| **Embedder** | Converts text → numbers (vectors) | `sentence-transformers` (local, free) |
| **Vector DB** | Stores vectors, finds similar ones fast | Pinecone / FAISS / ChromaDB / etc. |
| **LLM** | Reads retrieved chunks, writes the answer | Anthropic Claude |

Each role is independent — you can swap any one of them without touching the
others. For example, swap Pinecone for FAISS, or swap Claude for another LLM,
and the rest of the pipeline stays exactly the same.

---

## Why not just ask Claude directly without RAG?

| Without RAG | With RAG |
|---|---|
| Claude answers from its general training data | Claude answers from **your specific data** |
| Can hallucinate or be out of date | Grounded in the chunks you provided |
| No control over what knowledge it uses | You control exactly what context it sees |
| One model call | Embed → Search → Generate (3 steps) |

RAG is the standard pattern for building AI apps over private or up-to-date
documents — things like internal knowledge bases, product manuals, legal
documents, or any data Claude was not trained on.

---

## Summary in one sentence

> The vector DB finds the most relevant pieces of your data,
> and the LLM turns those pieces into a clear, readable answer —
> RAG is just the pipeline that connects the two.
