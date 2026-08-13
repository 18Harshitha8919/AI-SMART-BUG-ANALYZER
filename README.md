# CREATION OF INTELLIGENT BUG DIAGNOSIS PLATFORM WITH FIX RECOMMENDATION ASSISTANCE GROUP

**BugSense AI** is a production-quality, enterprise-grade AI-powered Bug Analysis & Root Cause Detection platform. It implements state-of-the-art Retrieval-Augmented Generation (RAG) and multi-agent workflows to automate bug triage, parse execution logs, retrieve historical duplicate reports, formulate root cause hypotheses, and deliver verified remediation playbooks.

---

## 📂 Project Structure

```text
smart-bug-analyzer/
│
├── client/                     # React + Vite + Tailwind Client Web App
│   ├── src/
│   │   ├── components/         # Navigation, Sidebar, layouts
│   │   ├── pages/              # Dashboard, SubmitBug, Analytics, KnowledgeBase
│   │   └── index.css, main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── server/                     # Node.js + Express API Gateway
│   ├── routes/                 # Express API routes (bugs, analytics, knowledge)
│   ├── db.js                   # Mongoose MongoDB database wrapper & JSON fallbacks
│   ├── logger.js               # Winston logging configurations
│   ├── package.json
│   └── index.js                # Express entrypoint
│
├── python-ai/                  # FastAPI AI Microservice
│   ├── agents/                 # LangGraph Multi-Agent Nodes (Triage, Log Analysis, etc.)
│   ├── controllers/            # Request orchestration controllers
│   ├── routes/                 # Router mappings
│   ├── schemas/                # Pydantic schemas (Agent outputs)
│   ├── main.py                 # FastAPI microservice entrypoint
│   ├── faiss_store.py          # FAISS Vector Indexing & NumPy Fallback manager
│   ├── Dockerfile
│   └── requirements.txt
│
├── uploads/                    # Uploaded bug logs/documents
├── docker-compose.yml          # Docker Compose configurations
├── requirements.txt            # System dependencies
└── README.md
```

---

## 🛠 Tech Stack

* **Frontend**: React.js, Vite, Tailwind CSS, Axios, Lucide Icons
* **Backend API Gateway**: Node.js, Express.js, Winston, Multer, Mongoose (MongoDB)
* **AI Core / RAG**: Python, FastAPI, SentenceTransformers (`all-MiniLM-L6-v2`), FAISS Vector Store, LangChain, LangGraph
* **LLM Engine**: Google Gemini API
* **Document Processing**: PyPDF2, python-docx, pandas
* **Databases**: MongoDB (with automated local JSON file fallback for offline runs)
* **Containerization**: Docker and Docker Compose

---

## 🚀 Setup & Execution Guide

### Option 1: Quick Start with Docker (Recommended)
Make sure you have Docker and Docker Compose installed, then execute:

1. Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
2. Spin up the containers:
   ```bash
   docker compose up --build
   ```
3. Once running, access the services:
   * **React Frontend**: `http://localhost:3000`
   * **Express Gateway**: `http://localhost:5000`
   * **FastAPI AI Server**: `http://localhost:8000`

---

### Option 2: Local Manual Setup

#### Step 1: Install & Boot Python AI service
1. Open a terminal in the root directory.
2. Initialize virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r python-ai/requirements.txt
   ```
4. Run the FastAPI microservice:
   ```bash
   python python-ai/main.py
   ```
   *FastAPI server will bind to `http://localhost:8000`.*

#### Step 2: Install & Boot Express Gateway Backend
1. Open a new terminal in the `server/` directory:
   ```bash
   cd server
   npm install
   npm start
   ```
   *Express server will bind to `http://localhost:5000`.*

#### Step 3: Install & Boot React Web Client
1. Open a new terminal in the `client/` directory:
   ```bash
   cd client
   npm install
   npm run dev
   ```
   *React client will bind to `http://localhost:3000`.*

---

## 🧪 E2E Performance Testing & Demonstrations
To execute the automated end-to-end testing suite validating the 12 core defect classes (including SQL deadlocks, memory leaks, timeouts, validation errors, etc.):
```bash
.\venv\Scripts\python python-ai/run_milestone4_tests.py
```
This runs the orchestration pipeline, indexes resolved tickets in FAISS/JSON, and outputs a comprehensive diagnostic evaluation report in **`milestone_4_test_report.md`**.
