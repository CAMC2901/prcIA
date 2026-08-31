# 🌍 Horizon Academy - Intelligent RAG Customer Service Assistant

An advanced AI-powered Customer Service Assistant designed for **Horizon Academy**, built using a **RAG (Retrieval-Augmented Generation)** architecture, **0-Token Static Interception Engine**, and **Custom Calculation Skills (MCP Standard)**.

It automatically answers frequently asked questions regarding prices, course levels, schedules, discounts, and enrollments based strictly on official business documentation, eliminating hallucinations and providing a human escalation flow via Google Forms.

---

## 🛠️ Key Architectural Components

### 1. **0-Token Static Response Engine (`backend/static_responses.py`)**
- Intercepts common user queries (greetings, schedule issues, human advisor requests, payment methods, placement tests, certificates, locations).
- Delivers instant answers in **0 milliseconds with ZERO token consumption**, drastically reducing API costs and latency.

### 2. **Custom Calculation Skills / MCP Standard (`backend/mcp_tools.py`)**
- Provides dynamic mathematical capabilities for complex academic business rules:
  - **`calculate_tuition_fee`**: Automatically computes module costs ($480k COP), registration fees ($60k COP), 10% Trimodular package discounts (for 3+ modules), and 5% Early Bird discounts.
  - **`calculate_placement_test_recommendation`**: Evaluates placement test scores (0-100 pts) and recommends the exact starting MCER level, required modules, and pedagogical advice.
  - **`calculate_total_course_hours`**: Calculates guided classroom hours (40h/module) and 24/7 self-study platform hours (20h/module) for any level or full program.
  - **`calculate_installment_plan`**: Computes 2-part or 3-part flexible bimestral payment plans for students paying per module.

### 3. **LangChain & RAG Pipeline (`backend/rag.py`)**
- Loads business text documents from `backend/data/` using `TextLoader`.
- Splits text into optimal chunks with `RecursiveCharacterTextSplitter` (chunk size: 500, overlap: 100).
- Manages strict system prompts (`PromptTemplate`) and few-shot examples.

### 4. **HuggingFace Embeddings (`all-MiniLM-L6-v2`)**
- Converts Spanish text into mathematical vector embeddings **100% locally and free of charge**.

### 5. **ChromaDB Vector Database (`chroma_db/`)**
- Local persistent vector store in the project root directory. Performs fast semantic similarity searches to retrieve the top 10 relevant document chunks per query.

### 6. **Google Gemini 2.5 Flash & Ollama Fallback**
- Primary LLM: **Google Gemini 2.5 Flash** (`gemini-2.5-flash`).
- Automatic Fallback: Seamlessly switches to a local **Ollama (`llama3`)** instance if Gemini API key fails or network is offline.

---

## 📁 Repository Structure

```text
prueba-ai/
├── backend/
│   ├── data/                 # Business documentation (.txt files)
│   ├── main.py               # FastAPI server (/api/chat, /api/metrics, /api/config)
│   ├── rag.py                # RAG Pipeline (LangChain + ChromaDB + Gemini/Ollama)
│   ├── static_responses.py   # 0-Token Interception Engine for common FAQs & support
│   ├── mcp_tools.py          # Custom calculation skills & MCP tools
│   ├── services.py           # In-memory Cache & Live Metrics Service
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Academy Landing Page + Clean Chat UI
│   ├── style.css             # White & Corporate Blue Theme + CSS Animations
│   └── main.js               # SPA logic, typing animations, REST API calls
├── chroma_db/                # Local Vector Database directory (persisted)
├── workflow_n8n.json         # Exported n8n automation workflow
├── .env.example              # Environment variables template
├── .gitignore                # Git secret protection
└── README.md                 # Technical documentation
```

---

## 🚀 Setup & Execution Guide

### Prerequisites
- **Python 3.9+**
- **Node.js 18+** & `npm`
- *(Optional)* **Ollama** installed with `llama3` (`ollama pull llama3`) for offline fallback.

---

### 1. Backend Setup (Python FastAPI)

1. Open a terminal in the project root and create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Create and configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   ESCALATION_FORM_URL=https://docs.google.com/forms/d/e/1FAIpQLSdAyhhqdotfhe9bwKaCC0faNaArmJLSjQOmuD9feRl0pEd95A/viewform
   ```

---

### 2. Frontend Setup (Vite / Vanilla JS)

In a second terminal, install frontend dependencies:
```bash
npm install
```

---

### 3. Running the Application

Start both servers concurrently:

#### **Terminal 1: Backend Server**
```bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 3000 --reload
```
*Backend API runs at `http://localhost:3000`.*

#### **Terminal 2: Frontend Web App**
```bash
npm run dev
```
*Frontend runs at `http://localhost:5173`.*

---

## 📊 Live Metrics & Cost Optimization

- **0-Token Cost Savings**: Intercepts greetings, support requests, and schedule questions directly without consuming LLM tokens.
- **In-Memory Cache**: Serves repeated queries instantly.
- **Real-Time Dashboard**: Tracks processed queries, cache hit rates, escalation rates, and estimated USD cost live on the frontend interface.
