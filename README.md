# Orion Governance AI

**Enterprise-grade, permission-aware semantic search backend with cloud-native RAG architecture**

Orion is a prototype semantic search and document intelligence system built for enterprise environments. It demonstrates the full lifecycle of an AI-powered knowledge retrieval system — from raw document ingestion through permission-filtered semantic search — using Google Cloud's AI and data services.

---

## What It Does

Orion enables organizations to search across their internal document repositories using natural language queries. Results are semantically ranked, citation-anchored, and filtered by user-level access permissions — modeling how enterprise systems enforce document visibility while delivering intelligent retrieval.

---

## Architecture Overview

```
Raw Documents (PDF, DOCX, Scanned)
        │
        ▼
┌─────────────────────┐
│   Ingestion Layer   │  Document AI (OCR) + Native Text Extraction
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Chunking & Schema  │  Page-anchored chunks with structural metadata + ACLs
└─────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│         Storage Layer            │
│  GCS (raw files)                 │
│  Firestore (metadata + chunks)   │
└──────────────────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Embedding Pipeline  │  Vertex AI Embeddings → Vector Index
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Retrieval Engine   │  Semantic similarity search + ACL-filtered results
└─────────────────────┘
```

---

## Key Features

### 1. End-to-End Document Processing Pipeline
- Ingests enterprise documents from local corpus simulating real repositories
- OCR processing via **Google Document AI** for scanned PDFs
- Native text extraction for digital PDFs and DOCX files
- Normalization into a canonical document schema with processing state tracking

### 2. Structural Chunking & Citation Anchoring
- Segments documents into semantically meaningful chunks
- Preserves page boundaries, character offsets, and section titles
- Enables precise source citations — critical for enterprise search reliability and auditability

### 3. Permission-Aware Access Control
- Document schema includes Access Control Lists (ACLs) per record
- Each chunk inherits permission metadata from its parent document
- Retrieval engine filters results by user identity at query time
- Models how production enterprise systems enforce document visibility

### 4. Multi-Layer Cloud Storage Architecture
- **Google Cloud Storage** — raw file persistence
- **Firestore** — metadata records, chunk subcollections, and lifecycle tracking
- Separation of raw content and structured metadata mirrors production document systems

### 5. Semantic Embedding & Retrieval
- Batch embedding workflow generates vectors for all document chunks via **Vertex AI**
- Working search pipeline accepts natural language queries and returns ranked, metadata-rich results
- Results include source filename, page ranges, and allowed users

### 6. Google Cloud Integration
| Service | Purpose |
|---|---|
| Vertex AI | Embeddings + LLM capabilities |
| Document AI | OCR for scanned documents |
| Cloud Storage | Raw document persistence |
| Firestore | Metadata and vector indexing |
| Google Drive API | Connector foundation (auth complete) |
| Google Calendar API | Connector foundation (auth complete) |

### 7. Connector Foundations
- OAuth authentication flow implemented for Google Drive and Google Calendar
- API connectivity verified; full sync logic planned for next phase

---

## Technical Skills Demonstrated

- Cloud-native architecture design (GCP)
- Information retrieval and semantic search
- Document processing pipelines (OCR + extraction)
- Vector embeddings and similarity ranking
- Access control modeling for enterprise environments
- RAG (Retrieval-Augmented Generation) backend components
- Modular Python project structure with production-ready practices

---

## Current Capabilities

| Capability | Status |
|---|---|
| Document ingestion pipeline | ✅ Complete |
| OCR and text extraction | ✅ Complete |
| Structural chunking | ✅ Complete |
| Metadata normalization | ✅ Complete |
| ACL permission modeling | ✅ Complete |
| Semantic embedding generation | ✅ Complete |
| Retrieval with citations | ✅ Complete |
| Cloud storage + Firestore persistence | ✅ Complete |
| Google Drive OAuth | ✅ Complete |
| Real-time Drive sync | 🔄 Planned |
| Hybrid keyword + semantic ranking | 🔄 Planned |
| Answer generation with citation grounding | 🔄 Planned |
| Audit logging and observability | 🔄 Planned |

---

## Roadmap

- **Hybrid Search** — Combine keyword and semantic ranking for improved precision
- **Answer Generation** — LLM response layer with strict citation grounding
- **Google Drive Sync** — Live permission mirroring from Drive to retrieval index
- **Audit Logging** — Full observability layer for compliance use cases
- **Incremental Indexing** — Efficient updates without full re-ingestion
- **Query Intent Routing** — Route queries to specialized retrieval strategies

---

## Project Structure

```
orion-governance-ai/
├── app/                  # Core application modules
├── scripts/              # Pipeline execution scripts
├── test_gcs.py           # GCS integration tests
├── test_vertex.py        # Vertex AI integration tests
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── .gitignore
```

---

## Setup

```bash
# Clone the repository
git clone https://github.com/gsatyabrata99/orion-governance-ai.git
cd orion-governance-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your GCP credentials and project settings
```

---

## What This System Represents

Orion demonstrates the foundational components required to build production enterprise search infrastructure: ingestion, indexing, permission-aware storage, and semantic retrieval. It is positioned as a **permission-aware semantic retrieval backend for enterprise knowledge systems** — the kind of system that sits beneath AI assistants deployed to thousands of employees.

---

*Built with Python · Google Cloud Platform · Vertex AI · Document AI · Firestore · Cloud Storage*
