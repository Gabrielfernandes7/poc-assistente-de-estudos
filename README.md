# BookSelfStudy 📚

BookSelfStudy is an educational platform designed to explore and understand the internal mechanics of **Retrieval-Augmented Generation (RAG)**. Inspired by Google NotebookLM, it allows users to upload documents and interact with them through a grounded AI assistant.

This project is a personal study initiative focused on implementing the entire RAG pipeline—from document ingestion to semantic search and local LLM generation—without relying on high-level "black-box" abstractions.

---

## ✨ Features

- **Multi-Notebook Support**: Isolate study contexts into dedicated notebooks (e.g., "Quantum Computing", "Exam Prep").
- **Robust Metadata Management**: Track notebook titles, creation dates, and preferred AI models via a persistent JSON registry.
- **Reference Management**: Upload and delete specific PDF or Markdown files per notebook.
- **Local AI Selection**: Choose between available Ollama models (Llama 3.2, Qwen, Mistral) dynamically.
- **Hallucination Mitigation**: Refined RAG prompts with strict grounding rules and increased context retrieval (k=5).
- **Persistent Vector Storage**: Each notebook has its own dedicated collection in **ChromaDB**.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: [React 19](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **API Client**: [Axios](https://axios-http.com/)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **LLM Engine**: [Ollama](https://ollama.com/)
- **Document Processing**: [PyMuPDF](https://pymupdf.readthedocs.io/)
- **Metadata**: JSON-based persistent registry.

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.10+)
- [Ollama](https://ollama.com/) installed and running locally.

### 1. Setup Ollama

Pull the models you wish to use:
```bash
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

### 2. Backend Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### 3. Frontend Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 🗺️ Project Structure

```text
.
├── backend/
│   ├── app/                # FastAPI application logic
│   │   ├── main.py         # API endpoints
│   │   ├── rag.py          # Core RAG logic (ChromaDB + Ollama)
│   │   └── metadata.py     # Notebook registry management
│   ├── chroma_db/          # Persistent vector storage
│   ├── uploads/            # Documents organized by {notebook_id}/
│   ├── notebooks_metadata.json # Global notebook registry
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.tsx         # Notebook-aware UI
    │   └── assets/         # Static assets
    └── package.json        # Frontend dependencies
```

---

## 📜 License

This project is for educational purposes. Feel free to explore, learn, and adapt for your own studies.
