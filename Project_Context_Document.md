# Shadow — AI Portfolio Assistant
## Project Context Document

**Owner:** Muhammad
**Assistant name:** Shadow
**Status:** Planning
**Last updated:** 2026-07-12

---

## 1. Overview

Shadow is a RAG-powered chatbot embedded on Muhammad's portfolio website. Its job is
to let recruiters ask natural-language questions about Muhammad — his experience,
projects, skills, and background — and get accurate, grounded answers pulled from a
curated knowledge base, not from the LLM's general training data.

Shadow speaks *about* Muhammad, not *as* Muhammad. Example: "Muhammad has built three
production RAG systems, most recently..." — not "I have built..."

## 2. Goals

- Answer recruiter questions accurately, using only Muhammad's curated knowledge base.
- Refuse gracefully ("I don't have that info — you can ask Muhammad directly at...")
  instead of hallucinating when the answer isn't in the knowledge base.
- Respond in under ~3 seconds for a typical query.
- Be trivial to update — Muhammad edits a markdown file, re-runs ingestion, done.
- Ship as a clean REST API any frontend (this portfolio, or a future one) can call.

## 3. Non-Goals (v1)

- Not a general-purpose chatbot — no coding help, no small talk beyond a greeting.
- No persistent cross-session memory (each session starts fresh).
- No user authentication — public, rate-limited endpoint.
- No voice interface.

## 4. Architecture

```
 ┌─────────────────┐        ┌──────────────────────┐
 │  React/Next.js   │  POST  │   FastAPI + Uvicorn   │
 │  portfolio site  │───────▶│   backend (Render/    │
 │  (chat widget)   │◀───────│   Railway)             │
 └─────────────────┘  JSON   └──────────┬────────────┘
                                          │
                        ┌─────────────────┼─────────────────┐
                        ▼                 ▼                 ▼
                ┌───────────────┐ ┌──────────────┐ ┌────────────────┐
                │ Embedding      │ │  Pinecone     │ │  Mistral API    │
                │ model (hosted  │ │  vector index │ │  (chat/         │
                │ on HF Hub)     │ │  (top-k match)│ │  generation)    │
                └───────────────┘ └──────────────┘ └────────────────┘
```

**Query flow:**
1. User asks a question in the chat widget → frontend POSTs to `/api/chat`.
2. Backend embeds the question using the HF-hosted embedding model.
3. Backend queries Pinecone for the top-k most relevant chunks from the knowledge base.
4. Backend builds a prompt: system persona + retrieved chunks + user question.
5. Backend calls the Mistral API for the final answer.
6. Backend returns `{ answer, sources }` to the frontend.

**Ingestion flow (offline, run manually or on a schedule):**
1. Read source docs from `/knowledge_base` — both the raw uploaded files in
   `/knowledge_base/files` (e.g. resume PDF/DOCX) and the narrative markdown
   files (`about.md`, `faq.md`).
2. Parse raw files to plain text first (PDF → `pypdf`/`pdfplumber`, DOCX →
   `python-docx`). Markdown files are already plain text.
3. Chunk text (e.g. ~300–500 tokens, some overlap).
4. Embed each chunk with the same HF embedding model used at query time.
5. Upsert vectors + metadata into Pinecone, tagging each chunk with its
   source filename (used later for the `sources` field in API responses).

> The embedding model **must** be identical at ingestion time and query time —
> mismatched embedding models will silently break retrieval quality.

## 5. Tech Stack

| Layer            | Choice                                  | Notes |
|-------------------|------------------------------------------|-------|
| Frontend           | React / Next.js                          | Existing portfolio, adds a chat widget component |
| Backend framework  | FastAPI + Uvicorn                        | Python; async-friendly for API calls |
| Backend hosting    | Render or Railway                        | Free/hobby tier is enough for v1 |
| Embedding model    | Open-source model hosted on Hugging Face Hub (e.g. `sentence-transformers/all-MiniLM-L6-v2`) | Called via HF Inference API, or downloaded and run inside the ingestion script |
| Vector database    | Pinecone (serverless index)              | One namespace is enough for v1 |
| LLM (generation)   | Mistral API (e.g. `mistral-small-latest`) | Grounded generation over retrieved context |
| Secrets management | `.env` locally, host's env var dashboard in prod | Never commit keys |

## 6. Repo Structure (proposed)

```
shadow/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, routes
│   │   ├── config.py            # env var loading
│   │   ├── rag/
│   │   │   ├── embed.py         # embedding calls
│   │   │   ├── retrieve.py      # Pinecone query logic
│   │   │   └── generate.py      # Mistral call + prompt template
│   │   └── schemas.py           # Pydantic request/response models
│   ├── ingestion/
│   │   ├── parse.py             # extracts text from PDF/DOCX resume uploads
│   │   ├── chunk.py
│   │   └── ingest.py            # run this to (re)build the Pinecone index
│   ├── requirements.txt         # include pypdf/pdfplumber + python-docx
│   ├── Dockerfile
│   └── .env.example
├── knowledge_base/
│   ├── files/                    # raw uploads — resume.pdf, etc. (not manually written)
│   │   └── resume.pdf
│   ├── about.md                  # narrative/tone content the resume doesn't cover
│   └── faq.md                    # common recruiter questions, written as Q&A
└── frontend/
    └── components/ShadowChat/    # chat widget, added to existing portfolio repo
```

## 7. API Contract

**POST `/api/chat`**
```json
// Request
{ "question": "What backend frameworks does Muhammad use?" }

// Response
{
  "answer": "Muhammad primarily works with FastAPI...",
  "sources": ["skills.md", "projects.md"]
}
```

**GET `/api/health`** → `{ "status": "ok" }`

## 8. Environment Variables

| Variable              | Purpose                                 |
|------------------------|------------------------------------------|
| `MISTRAL_API_KEY`      | Mistral API auth                        |
| `PINECONE_API_KEY`     | Pinecone auth                           |
| `PINECONE_INDEX_NAME`  | Target index                            |
| `HF_TOKEN`             | Hugging Face Inference API auth (if used instead of local model) |
| `EMBEDDING_MODEL_NAME` | Must match between ingestion and query  |
| `ALLOWED_ORIGINS`      | CORS — restrict to portfolio domain     |

## 9. Knowledge Base Content Plan

Two-tier approach:
- **`knowledge_base/files/`** — raw resume upload (PDF or DOCX). Parsed and chunked
  automatically by the ingestion script; covers roles, dates, hard skills, education.
- **`about.md` / `faq.md`** — short, hand-written markdown covering what a resume
  doesn't: tone, career narrative, working style, what Muhammad is looking for next,
  and direct answers to common recruiter questions ("why did you leave X",
  "are you open to remote"). Write these in third person about Muhammad, one
  self-contained fact/answer per paragraph so chunking doesn't split ideas apart.

## 10. Success Criteria

- Recruiter can ask 10 realistic questions and get correct, grounded answers for the
  ones covered by the knowledge base, and an honest "I don't know" for the rest.
- End-to-end latency under ~3s on a warm backend.
- Adding a new fact = editing one markdown file + re-running ingestion, no code changes.

## 11. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Hallucination | Strict system prompt: "only answer from provided context; otherwise say you don't know" |
| Embedding/query model mismatch | Store `EMBEDDING_MODEL_NAME` as a config constant used by both ingestion and query code |
| Free-tier cold starts (Render/Railway) | Acceptable for v1; document it, revisit if it's a UX problem |
| API cost/rate limits | Cache repeated questions if needed later; not required for v1 |

## 12. Future Work (out of scope for v1)

- Multi-turn conversation memory
- Analytics on what recruiters ask
- Voice input/output
- Swap Mistral for a fine-tuned open model if cost/latency demands it
