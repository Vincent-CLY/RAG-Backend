# 🚀 RAG-Backend: Personal Profile & Job Application AI Assistant

[ English ] | [ [繁體中文 / 粵語](./README.zh-HK.md) ] | [ [📖 Architecture Notes & Technical Glossary](./NOTES.md) ]

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Java 21](https://img.shields.io/badge/Java-21+-ED8B00.svg?logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Gateway-Spring%20Boot%203.3-6DB33F.svg?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Virtual Threads](https://img.shields.io/badge/Concurrency-Virtual%20Threads-007396.svg)](https://openjdk.org/jeps/444)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/VectorDB-Qdrant-DC382D.svg?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![LangChain](https://img.shields.io/badge/Framework-LangChain-1C3C3C.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/Agents-LangGraph-1C3C3C.svg)](https://langchain-ai.github.io/langgraph/)
[![LangSmith](https://img.shields.io/badge/Observability-LangSmith-FF6F00.svg)](https://smith.langchain.com/)
[![Docling](https://img.shields.io/badge/Document%20Parser-Docling-052FAD.svg)](https://github.com/DS4SD/docling)
[![MCP](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol-4B0082.svg)](https://modelcontextprotocol.io/)

A multi-stage, production-grade Retrieval-Augmented Generation (RAG) backend engineered for personal knowledge vault management, intelligent job application tailoring, and Model Context Protocol (MCP) server integration.

This system ingests diverse document types (resumes, portfolios, research papers, presentations, spreadsheets, charts, scanned forms), preserves structural layout integrity, exposes deterministic REST APIs via FastAPI, and connects natively to external AI clients (e.g., Claude Desktop, Cursor) via MCP.

---

## 🎯 Project Vision & Goals

1. **Personal Profile Knowledge Vault**: Digitize resumes, portfolios, certifications, and technical projects across multiple formats (PDF, PPTX, DOCX, XLSX, HTML, images, audio/video).
2. **AI Job Application Copilot**: Parse target Job Descriptions (JDs), perform gap analysis against the candidate profile, generate tailored bullet points (STAR method), and practice interview Q&A.
3. **Plug-and-Play MCP Server**: Expose retrieval endpoints as a standardized MCP server, allowing any MCP-compliant LLM client to query personal data securely.
4. **Learning-by-Building AI Engineering**: Bridge foundational LLM theory with production engineering practices (schema validation, hybrid retrieval, agentic state machines, and observability).
5. **Bilingual Polyglot Architecture**: Combine Python's unrivaled AI/ML ecosystem with Java's high-concurrency Virtual Threads gateway — each language owning the layer it is best at.

---

## 🏗️ Polyglot Architecture: Which Language Owns Which Layer?

A deliberate **separation of concerns**: Java's Virtual Threads own the **edge/control plane** (security, routing, rate-limiting, observability); Python owns the **AI/data plane** (parsing, retrieval, agents, generation).

```
External Client (Web / Bot / Claude Desktop / n8n / Dify)
        │
        ▼
╔═══════════════════════════════════════════════════════════╗
║  Java 21+ Spring Boot 3.3 (WebFlux / Virtual Threads)      ║  ← Control Plane / Edge
║  • spring.threads.virtual.enabled=true                     ║
║  • Spring Security + JWT / OAuth2 (authN/authZ)            ║
║  • Rate limiting / quotas / multi-tenant (Resilience4j)    ║
║  • Request routing / API composition / BFF                 ║
║  • WebClient (non-blocking) → Python AI Core               ║
║  • Kafka / RabbitMQ async ingest queue                     ║
║  • Micrometer + Prometheus + Grafana + OpenTelemetry       ║
╚═══════════════════════════════════════════════════════════╝
        │  REST / gRPC (with W3C trace context)
        ▼
╔═══════════════════════════════════════════════════════════╗
║  Python FastAPI — AI Core / Data Plane (async)            ║
║  • Docling parsing → LlamaIndex / Qdrant retrieval        ║
║  • Hybrid + Multi-query + HNSW + RRF + Two-Stage Rerank   ║
║  • LangGraph Multi-Agent (MoA)                            ║
║  • LLM generation + Guardrails                            ║
╚═══════════════════════════════════════════════════════════╝
        │
        ▼
  Qdrant (vectors) + PostgreSQL (metadata/state) + Redis (cache/queue)
```

| Concern | Language / Tech | Why it belongs here |
| :--- | :--- | :--- |
| **Auth / Security** | Java Spring Security | Mature enterprise OAuth2/JWT/SSO + JVM auditing |
| **Rate limiting / quotas / multi-tenancy** | Java (Resilience4j/Bucket4j) | Precise quota control under high concurrency |
| **API gateway / BFF / routing** | Java Spring WebFlux | Non-blocking edge, absorbs heavy concurrent load |
| **Async ingest queue** | Java + Kafka/RabbitMQ | Offload heavy parsing, protect the AI Core |
| **Observability (JVM layer)** | Java Micrometer/Prometheus | JVM metrics + OpenTelemetry spans across both tiers |
| **Document parsing** | Python (Docling) | Unrivaled AI/ML ecosystem |
| **Vector retrieval / reranking** | Python (LlamaIndex/Qdrant) | Python dominates the RAG retrieval stack |
| **Multi-Agent orchestration** | Python (LangGraph) | Agent frameworks are native to Python |
| **LLM generation / Guardrails** | Python | Strongest LLM SDK + prompt engineering ecosystem |

> ⚠️ **Anti-over-engineering note**: Two runtimes add complexity. For a solo/personal project, ship **V1–V3 in pure Python first**, then introduce the Java gateway (V4) when you need enterprise-grade security, quotas, or JVM-ecosystem integration. See [NOTES.md §6.9](./NOTES.md) for the full ADR.

---


## 🗺️ 6-Stage Evolution Roadmap (Python + Java Hybrid)

```
[Version 1: Foundation RAG, Validation & API Gateway]
Docling / Tesseract ➔ Layout-Aware Chunking ➔ LangChain + Qdrant ➔ FastAPI + Pydantic ➔ LangSmith Tracing

                                      ▼

[Version 2: Multimodal Ingestion, LlamaIndex Indexing & Hybrid Search]
Whisper Audio/Video ➔ LlamaIndex Hierarchical Indexing ➔ Qdrant Hybrid Search (Dense + BM25) ➔ Reranker ➔ JD Matcher

                                      ▼

[Version 3: LangGraph Agentic Workflows & MCP Ecosystem]
LangGraph State Machine (Self-RAG / Routing) ➔ FastMCP Server (Claude / Cursor) ➔ Docker & Cloud Deployment

                                       ▼

[Version 4: Java + Python Hybrid Gateway (Virtual Threads)]
Java 21 Spring Boot WebFlux (Virtual Threads) Edge/Gateway ➔ Security + Rate-Limiting ➔ Kafka async ingest ➔ REST/gRPC ➔ Python AI Core ➔ OpenTelemetry tracing

                                       ▼

[Version 5: Mixture-of-Agents Chatbot]
LangGraph MoA: Orchestrator ➔ Researcher / Logic Analyst / Challenger / Solver ➔ Coding Experts Team (custom skills) ➔ Model Routing ➔ n8n / Dify integration

                                       ▼

[Version 6: Fine-tuning & Distillation (Nemotron-4)]
QLoRA domain adaptation ➔ Nemotron-4 Reward Model ➔ DPO/SteerLM alignment ➔ Minitron distillation ➔ RAGAS-gated release
```

---

## 📦 Version Breakdown & Technical Architecture

### 🔹 Version 1: Foundation RAG, Validation & API Gateway
Focuses on high-fidelity document parsing, deterministic data schemas, vector storage, API access, and observability.

#### Tech Stack
* **Parsing & Extraction**: `Docling` (IBM layout analysis model), `Tesseract OCR` (fallback for scanned images), `openpyxl`, `python-docx`
* **Orchestration**: `LangChain` (v0.3+ / 1.x LCEL pipelines)
* **Data Contracts**: `Pydantic v2`
* **Vector Database**: `Qdrant` (in-memory, local persistent, or Qdrant Cloud Free Tier)
* **API Framework**: `FastAPI` + `uvicorn` (interactive Swagger UI at `/docs`)
* **Observability & Tracing**: `LangSmith`
* **Package Management**: `uv`

#### Detailed Steps & Sub-steps
* **Step 1.1: Multi-Format Document Ingestion & Parsing**
  * `1.1.1 Format Ingestion`: Read PDF, PPTX, DOCX, XLSX, HTML, Markdown, and raw text files.
  * `1.1.2 Layout Detection`: Use Docling to detect column layouts, reading sequences, and section headers (H1/H2/H3).
  * `1.1.3 Table Recovery`: Convert complex data tables into clean Markdown/HTML tables without row/column loss.
  * `1.1.4 Visual Binding`: Extract embedded figures and bind them to their corresponding captions and textual legends.
* **Step 1.2: Layout-Aware Chunking & Metadata Enrichment**
  * `1.2.1 Hierarchical Chunking`: Chunk text based on document outline hierarchies rather than arbitrary character lengths.
  * `1.2.2 Atomic Block Preservation`: Ensure tables, code snippets, and figure descriptions are never split across chunks.
  * `1.2.3 Metadata Injection`: Stamp each chunk with `source_file`, `page_number`, `document_type`, and `timestamp`.
* **Step 1.3: Vector Embedding & Storage in Qdrant**
  * `1.3.1 Dense Embedding Generation`: Generate 1536-dimensional embeddings using `text-embedding-3-small`.
  * `1.3.2 Collection Setup`: Configure Qdrant collection with Cosine distance metric and HNSW indexing parameters.
  * `1.3.3 Payload Indexing`: Create payload indexes for metadata fields to enable millisecond metadata filtering.
* **Step 1.4: Base Retrieval & Question Answering Pipeline**
  * `1.4.1 Top-K Semantic Search`: Retrieve top-k relevant chunks using cosine similarity search.
  * `1.4.2 System Prompting`: Craft grounded prompts with anti-hallucination guardrails and source citation instructions.
  * `1.4.3 Grounded Generation`: Synthesize contextual responses using `gpt-4o-mini` / `gpt-4o`.
* **Step 1.5: Pydantic Validation & FastAPI Gateway**
  * `1.5.1 Schema Definition`: Enforce strict contracts on incoming queries (`RAGRequest`) and responses (`RAGResponse`).
  * `1.5.2 RESTful Endpoints`: Expose `/query` (answer query with citations), `/ingest` (upload and process files), and `/health`.
  * `1.5.3 Swagger UI Documentation`: Interactive testing interface accessible via `/docs` for bot and client testing.
* **Step 1.6: Observability with LangSmith**
  * `1.6.1 Zero-Code Tracing`: Configure environment variables for seamless trace logging.
  * `1.6.2 Trace Analysis`: Monitor chunk retrieval relevance, prompt construction, LLM latency, and token expenditures.



---

### 🔹 Version 2: Multimodal Ingestion, LlamaIndex Indexing & Hybrid Search
Focuses on extending inputs to audio/video, introducing LlamaIndex advanced indexing strategies, hybrid lexical-semantic search, and candidate-job matching.

#### Tech Stack
* **Audio/Video Transcription**: `OpenAI Whisper` / `faster-whisper`, `ffmpeg-python`
* **Advanced Indexing**: `LlamaIndex` (`llama-index-core`, `llama-index-readers-docling`, `llama-index-vector-stores-qdrant`)
* **Vector & Lexical Storage**: `Qdrant` (Dense embeddings + Sparse BM25 / SPLADE vectors)
* **Reranking**: `flashrank` or `BAAI/bge-reranker-large` (Cross-Encoder)
* **Job Matching Engine**: Custom Python matching logic + Pydantic scoring models

#### Detailed Steps & Sub-steps
* **Step 2.1: Multimodal Audio & Video Processing**
  * `2.1.1 Audio Extraction`: Extract high-fidelity audio streams from project demo videos and recorded presentations.
  * `2.1.2 Timestamped Transcription`: Transcribe speech with Whisper, producing timestamped dialogue segments.
  * `2.1.3 Multimodal Ingestion`: Associate transcript segments with project portfolio metadata and ingest into Qdrant.
* **Step 2.2: LlamaIndex Advanced Indexing Engine**
  * `2.2.1 Sentence-Window Retrieval`: Index single sentences as vectors; during query time, expand context to include neighboring sentences.
  * `2.2.2 Parent-Child Node Parsing`: Search granular child chunks for precise semantic matching, while returning parent sections to the LLM.
* **Step 2.3: Hybrid Search (Dense + Sparse) & Cross-Encoder Reranking**
  * `2.3.1 Sparse Vector Extraction`: Compute BM25 lexical weights to match exact keywords (company names, tools, acronyms).
  * `2.3.2 Reciprocal Rank Fusion (RRF)`: Fuse dense semantic scores with sparse lexical scores natively inside Qdrant.
  * `2.3.3 Cross-Encoder Reranking`: Re-score top-20 retrieved candidates using a Cross-Encoder to output the most pertinent top-5.
* **Step 2.4: Automated Job Matching & Skill Gap Analysis**
  * `2.4.1 JD Schema Extraction`: Parse target Job Descriptions into required skills, preferred qualifications, and responsibilities.
  * `2.4.2 Compatibility Matrix Calculation`: Compare JD requirements against user profile chunks and generate a gap report.
  * `2.4.3 Tailored Application Advice`: Generate STAR-method interview talking points aligned with the target position.

---

### 🔹 Version 3: LangGraph Agentic Workflows & MCP Ecosystem
Transitions static pipelines into dynamic, autonomous agents with self-correction capabilities, exposed globally through the Model Context Protocol.

#### Tech Stack
* **Agentic Framework**: `LangGraph` (StateGraph, conditional routing, human-in-the-loop)
* **Model Context Protocol**: `FastMCP` / `mcp` SDK (Anthropic standard)
* **Containerization & Deployment**: `Docker`, `Docker Compose`, `Fly.io` / `Render` / `Hugging Face Spaces`

#### Detailed Steps & Sub-steps
* **Step 3.1: LangGraph Autonomous Workflow Engine**
  * `3.1.1 State Schema Definition`: Maintain shared state (query history, intent, retrieved docs, retry counters, evaluation scores).
  * `3.1.2 Dynamic Query Routing`: Direct queries to specialized paths (Profile Inspection, JD Gap Analysis, General Q&A).
  * `3.1.3 Self-RAG & Query Rewriting`: Automatically assess chunk relevance; rewrite search queries if retrieval confidence is low.
  * `3.1.4 Hallucination & Factuality Guard`: Compare generated answers against reference chunks before delivering output.
* **Step 3.2: Model Context Protocol (MCP) Server Integration**
  * `3.2.1 MCP Tools Implementation`: Expose tools like `search_resume()`, `get_project_details()`, `evaluate_job_fit()`.
  * `3.2.2 MCP Resources Implementation`: Expose candidate resume Markdown and technical case studies as readable resources.
  * `3.2.3 Client Integrations`: Provide ready-to-use configuration files for Claude Desktop and Cursor IDE.
* **Step 3.3: Production Containerization & Cloud Deployment**
  * `3.3.1 Multi-Stage Dockerfile`: Build lightweight, secure container images separating build dependencies from runtime.
  * `3.3.2 Compose Orchestration`: Orchestrate FastAPI backend and Qdrant vector database via `docker-compose.yml`.
  * `3.3.3 Cloud Deployment & Live Demo`: Deploy to cloud hosting with continuous monitoring and SSL termination.

---

## 🛠️ Quickstart & Development Setup

### Prerequisites
* **Python**: `3.11+`
* **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended for fast virtual environment management)
* **Qdrant**: Local Docker instance or free [Qdrant Cloud](https://cloud.qdrant.io/) cluster

### 1. Clone & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/Vincent-CLY/RAG-Backend.git
cd RAG-Backend

# Install dependencies using uv
uv sync
```

### 2. Configure Environment Variables
Copy the example environment file and fill in your keys:
```bash
cp .env.example .env
```
Ensure the following variables are configured:
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=http://localhost:6333
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=rag-backend
```

### 3. Launch Local Qdrant (Optional if using Cloud)
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### 4. Run the API Server
```bash
uv run uvicorn main:app --reload --port 8000
```
Open your browser and navigate to `http://localhost:8000/docs` to test endpoints via the interactive Swagger UI!

---

## 📖 Deep-Dive Notes & Learning Guide

Want to understand the reasoning behind these technical decisions?
👉 Read our comprehensive [**Architecture Notes & Technical Glossary (NOTES.md)**](./NOTES.md) covering:
* End-to-end RAG pipelines explained from first principles.
* Keyword Search vs. Vector Search vs. Hybrid Search vs. Rerankers.
* Why Docling layout chunking and LlamaIndex sentence-window chunking complement each other.
* The "Golden Combination": How LlamaIndex, Qdrant, and LangGraph work together without overlap.
* An accessible AI Developer glossary breaking down confusing technical jargon.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).

