# AI Smart Bug Analyzer and Fix Advisor

**AI Smart Bug Analyzer and Fix Advisor** is a production-quality, enterprise-grade AI-powered Bug Analysis & Root Cause Detection platform. In **Milestone 1**, we establish the core platform foundation: a React frontend dashboard with dark/light mode states, an Express.js API gateway, a FastAPI Python AI microservice, and a working FAISS vector RAG pipeline.

---

## 📂 Project Structure

```text
smart-bug-analyzer/
│── client/                    # React + Vite + Tailwind Client Web App
│   ├── src/
│   │   ├── components/        # Sidebar, custom layout tools
│   │   ├── pages/             # Dashboard, SubmitBug, KnowledgeBase, Architecture, Docs
│   │   └── index.css, main.tsx
│   ├── package.json
│   └── vite.config.ts
│── server/                    # Node.js + Express Gateway
│   ├── routes/                # API router mapping
│   ├── db.js                  # Mongoose MongoDB wrapper & local file fallbacks
│   ├── logger.js              # Winston logging config
│   ├── package.json
│   └── index.js               # Express entrypoint
│── python-ai/                 # FastAPI AI Microservice
│   ├── main.py                # FastAPI routing & file parsers (PyPDF2, python-docx, pandas)
│   ├── faiss_store.py         # FAISS Vector Indexing & NumPy Fallback manager
│   └── requirements.txt
│── knowledgebase/             # Compilation Seeder scripts
│   └── seed_kb.py             # FAISS indexing bootstrapping seeder
│── datasets/                  # Seed dataset collection folder
│   └── historical_bugs.json   # Mozilla, Apache, Eclipse, Linux JSON dataset
│── uploads/                   # Local multer upload directory
│── docs/                      # Technical specification layout documentation
│   └── design_doc.md          # Vector math, workflow graphs, schemas
└── README.md
```

---

## 🛠 Tech Stack

- **Frontend**: React.js, Vite, Tailwind CSS, Axios, Lucide Icons
- **Backend Gateway**: Node.js, Express.js, Winston, Multer, Mongoose (MongoDB)
- **AI Core**: Python, FastAPI, SentenceTransformers (`all-MiniLM-L6-v2`), FAISS, PyPDF2, python-docx, pandas
- **Local Fallbacks**: Standard local JSON file database for offline runs when MongoDB is not active.

---

## 🚀 Setup & Execution Guide

### Prerequisite Checklist
1. **Python 3.10+** (with virtual environment support)
2. **Node.js 18+** & **npm**
3. **MongoDB** (Optional. Server has automated local file database fallback if offline)

---

### Step 1: Install & Seed Python AI service
1. Open a terminal in the project directory.
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
4. Build the vector database and compile the FAISS index:
   ```bash
   python knowledgebase/seed_kb.py
   ```
5. Run the FastAPI microservice:
   ```bash
   python python-ai/main.py
   ```
   *FastAPI server will bind to `http://localhost:8000`.*

---

### Step 2: Install & Boot Express Gateway Backend
1. Open a *new* terminal in the `server/` directory:
   ```bash
   cd server
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Launch gateway API server:
   ```bash
   npm start
   ```
   *Express server will bind to `http://localhost:5000`.*

---

### Step 3: Install & Boot React Web Client
1. Open a *new* terminal in the `client/` directory:
   ```bash
   cd client
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Launch development client web app:
   ```bash
   npm run dev
   ```
   *React client will bind to `http://localhost:3000`.*

---

## 🧪 RAG Ingestion Pipeline Flow

1. Navigate to the Web UI at `http://localhost:3000`.
2. Go to **Submit Bug** tab.
3. Drop a server log file (`.log`, `.txt`) or documents (`.pdf`, `.docx`, `.csv`) inside the upload zone. The gateway parses text using Python AI parsers and populates trace forms.
4. Click **Submit to RAG Grid**.
5. The gateway will:
   - Generate ID `BUG-XXXX`.
   - Normalize characters and compress spacing.
   - Embed text and query the FAISS database.
   - Run duplicate detection (similarity index threshold check at >90%).
   - Return matches and success metrics.
6. The dashboard list updates instantly!
