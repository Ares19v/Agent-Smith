# EVAL — Agent Smith

> **Evaluation Date:** 2026-05-29
> **Evaluator:** Automated Portfolio Review
> **Maturity Level:** MVP

---

## 1. Project Purpose & Problem Statement

Agent Smith is a local-first, privacy-preserving AI orchestration platform designed to run multiple specialized AI agents entirely on-premises — no cloud subscriptions, no data leakage. The platform lets users dynamically create, train, and converse with purpose-built intent agents, each powered by a local ML pipeline. The target audience is developers and small organizations that need flexible chatbot infrastructure but cannot tolerate sensitive data transiting third-party APIs. It fills a real gap: most agent platforms (LangChain, CrewAI) depend on cloud LLMs, while Agent Smith makes the local-first case using classical ML for the hot path.

---

## 2. Technical Architecture

Agent Smith is a two-container microservice system: an **Nginx Alpine** container serves the vanilla JS SPA and reverse-proxies `/api/` calls to a **FastAPI** backend running on Python 3.10+. The frontend communicates asynchronously via `fetch`.

The core intelligence lives in `core_engine.py`:
- **`IntentAgent`** — wraps a `scikit-learn` pipeline of `TfidfVectorizer` (English stop-word filtered) feeding into an `MLPClassifier` (two hidden layers: 32 and 16 units). Each agent stores its training data as a JSON file in `agents_data/`.
- **`AgentManager`** — a singleton that auto-discovers agent JSON files, instantiates `IntentAgent` objects, hot-reloads on CRUD changes, and manages a shared RAG document context.
- **Document Context** — PDF, DOCX, and TXT uploads are parsed and injected into a global context string, grounding agent responses.
- **LLM Fallback** — when MLP confidence drops below a configurable threshold, the system optionally routes to Groq, OpenAI, or Ollama; these stubs are disabled by default, keeping everything offline.

API is thin: list/create/delete agents, chat, upload documents, and a health probe. Docker Compose ties the two containers together behind a single port 80 interface.

---

## 3. Model/Algorithm Details

The intent classification pipeline uses:
- **TF-IDF Vectorization**: Converts raw utterances into sparse token-frequency vectors, removing English stop-words. No subword tokenization — this is a deliberate trade-off for speed and interpretability over accuracy on complex phrasing.
- **MLPClassifier (scikit-learn)**: Two hidden layers (32→16 units), trained on per-agent JSON intent datasets. The network outputs class probabilities; a confidence threshold gates whether to trust the local result or fall back to an LLM.
- **Inference mode**: Fully synchronous, CPU-bound — suitable for low-concurrency local usage. No GPU required.
- **RAG layer**: Document context is string-injected into the agent response rather than being vector-retrieved, making this a "context stuffing" approach rather than a true semantic retrieval system.

---

## 4. Strengths

- **Complete offline operation** — all inference runs locally with zero external API dependencies by default.
- **Hot-reload capability** — agents can be created, trained, or deleted without restarting the server.
- **Clean microservice split** — Nginx/FastAPI separation follows production patterns; Docker Compose orchestration is well-structured.
- **Security posture** — enforces path traversal prevention, MIME validation, file-size limits, and safe agent-name regex constraints.
- **LLM fallback hook** — gracefully degrades to cloud LLMs when local confidence is insufficient, making it extensible.
- **CI/CD pipeline** — `.github/workflows/ci.yml` provides automated build and linting.
- **Windows-friendly automation** — `INSTALL.bat`, `Run_Project.bat`, `UNINSTALL.bat` make local setup trivial.

---

## 5. Limitations & Known Gaps

- **TF-IDF + MLP ceiling** — this pipeline degrades on paraphrase, synonym variation, or out-of-vocabulary phrasing. Modern embedding-based classifiers (e.g., sentence-transformers) would significantly improve intent matching without sacrificing offline operation.
- **Context stuffing is not true RAG** — documents are injected as raw strings. Long documents will silently truncate or pollute context with irrelevant content. A proper vector store + semantic chunking pipeline is needed.
- **Session memory is in-process** — conversation history lives in RAM, so restarts clear all sessions. No persistence layer for history.
- **Vanilla JS frontend** — no component framework makes the UI hard to extend or test reliably; already shows its limits in scalability.
- **Single-process concurrency** — Uvicorn default worker; no task queue for heavy ML training workloads.
- **No authentication** — the API has zero auth; anyone on the same network can create/delete agents or exfiltrate documents.
- **Test coverage** — no visible test suite beyond what GitHub Actions runs; no pytest suite documented.

---

## 6. Code Quality Assessment

**Structure**: Clean separation between `api.py` (routes), `core_engine.py` (ML logic), and the frontend static layer. The `AgentManager` singleton pattern is appropriate for this scale.

**Documentation**: README is thorough, includes a Mermaid architecture diagram, API reference table, and example `curl` request. `ARCHITECTURE.md` adds useful design rationale.

**Tests**: A CI workflow exists but specific test targets are not documented in the README. No pytest suite is referenced.

**Docker**: Both `Dockerfile`s exist with a working `docker-compose.yml`. This is a genuine production pattern.

**Security**: Input sanitization is mentioned explicitly, which is commendable for a side project. Secrets live in `.env` (gitignored).

**Overall quality**: Above average for a solo portfolio project. The main gap is formal test coverage.

---

## 7. Maturity Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| Functionality | 7/10 | Core intent routing works; RAG and fallback are partial/stub |
| Code Quality | 7/10 | Clean, well-structured; missing formal tests |
| Documentation | 8/10 | Strong README + ARCHITECTURE.md; lacks API schema docs |
| Scalability | 5/10 | Single process, in-memory sessions, no auth |
| Security | 6/10 | Good input validation; zero API authentication is a red flag |
| **Overall** | **6.5/10** | Solid MVP with clear upgrade path |

---

## 8. Suggested Next Steps

1. **Replace TF-IDF with sentence-transformers embeddings** — drop `scikit-learn` classifier and use a local embedding model (e.g., `all-MiniLM-L6-v2`) with cosine similarity. This would dramatically improve paraphrase handling without breaking the offline-first promise.
2. **Add API authentication** — implement JWT-based or API-key auth on all `/api/` routes. Without this, the platform cannot be safely deployed even on a LAN.
3. **Implement true vector RAG** — integrate a lightweight local vector store (ChromaDB or FAISS) for document retrieval instead of context stuffing. Chunking + semantic search would make the document upload feature genuinely useful.

---

## 9. Verdict

Agent Smith is a well-engineered local-first AI orchestration MVP that demonstrates strong understanding of microservice architecture and production deployment patterns. The classical ML pipeline (TF-IDF + MLP) is honest about its limitations and the LLM fallback hook shows architectural foresight. However, the lack of API authentication, absence of a formal test suite, and the shallow RAG implementation hold it back from being a production-ready system. It stands as an impressive solo portfolio piece that is one authentication layer and one embedding upgrade away from being genuinely deployable.

---
<p align="center">Made by Devansh Tyagi @ 2026</p>
