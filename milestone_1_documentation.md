# Technical Documentation: Milestone 1 (RAG Ingestion & Similarity Retrieval)

This document provides complete technical documentation for the core ingestion pipeline, vector embeddings, semantic retrieval, and duplicate detection layers built in **Milestone 1** of the **AI Smart Bug Analyzer and Fix Advisor (BugSense AI)** platform.

---

## 1. Objective & Value Proposition
Milestone 1 builds the foundation of the platform:
* **Automatic Document Ingestion**: Parses crash logs, PDFs, Word docs (`.docx`), and CSVs to extract error stack text automatically.
* **Semantic Code Search (RAG)**: Converts unstructured crash logs into high-dimensional vectors to search a historical knowledge base of resolved bugs.
* **Instant Duplicate Mitigation**: Instantly flags new incoming defects that match existing records with $>90\%$ semantic similarity to prevent redundant ticket triage.

---

## 2. Core Architecture Components

### A. Document Text Parsers (`python-ai/main.py`)
Exposed via the `/process-file` endpoint on the FastAPI backend:
1. **Raw Log / Text Files (`.log`, `.txt`)**: Read as direct string inputs with UTF-8 decoding fallbacks.
2. **Portable Document Formats (`.pdf`)**: Extracted recursively using `PyPDF2.PdfReader` to reconstruct text blocks.
3. **Word Documents (`.docx`)**: Extracted paragraph-by-paragraph using the `docx` library.
4. **CSV Tables (`.csv`)**: Loaded into `pandas.DataFrame` and formatted directly into markdown table notation (making it readable for LLMs and developers).

### B. Embedding & FAISS Vector Index (`python-ai/faiss_store.py`)
1. **Model**: SentenceTransformer `all-MiniLM-L6-v2` running locally in the caching folder (`./embeddings/cache`).
   * Converts variable-length text reports into a **384-dimensional dense vector representation**:
     $$\mathbf{v} \in \mathbb{R}^{384}$$
2. **Index Structure**: Facebook AI Similarity Search (FAISS) utilizing `IndexFlatIP` (Flat Inner Product index measuring cosine similarity).
3. **Storage**: The vector index is stored as a flat binary file `embeddings/faiss_index.bin` alongside JSON metadata mapping to database keys.

### C. Similarity Search & Duplicate Logic (`python-ai/main.py` & `/search`)
1. An incoming bug's title, description, and stack trace are concatenated and vectorized.
2. The query vector is scanned against the FAISS index:
   $$\text{Similarity Score} = \sum_{i=1}^{384} q_i d_i$$
3. If the top match score is **$>0.90$ (90%)**, the Express gateway tags the issue status as a **`Potential Duplicate Bug`** and returns the matching historical bug ID.

### D. Multi-Tier Database Failover (`server/db.js`)
* **Primary Store**: MongoDB.
* **Local Resilient Fallback**: Standard JSON flat file database system (`bugs.json`). 
* If MongoDB connections timeout (e.g., port 27017 blocked), the server automatically switches to local file systems in under **3 seconds**, preventing client crashes.

---

## 3. Core Ingestion Endpoints (Express Gateway)

* **`POST /api/submitBug`**: Cleans the input strings, computes embeddings via Python, runs the FAISS duplicate check, queries agent orchestrations, and saves the document.
* **`GET /api/bugs`**: Returns a list of all active tickets.
* **`GET /api/similar/:id`**: Returns the top matching resolved bugs from the FAISS database for the selected ticket.
* **`POST /api/upload`**: Temporary file buffer upload gateway.

---

## 4. UI Dashboard Foundations (`client/src/`)
* Built with a custom React application styled with responsive **Vanilla Tailwind CSS**.
* Contains a main table grid, status stats, theme toggle buttons, and form validation blocks.
