# BookSelfStudy 📚

BookSelfStudy is an educational platform designed to explore and understand the internal mechanics of **Retrieval-Augmented Generation (RAG)**. Inspired by Google NotebookLM, it allows users to upload documents and interact with them through a grounded AI assistant.

This project is a personal study initiative focused on implementing the entire RAG pipeline—from document ingestion to semantic search and local LLM generation—without relying on high-level "black-box" abstractions.

---

## ✨ Features

- **Document Ingestion**: Support for PDF and Markdown files.
- **Smart Chunking**: Automatic text extraction and segmenting with configurable overlap for context retention.
- **Vector Storage**: Persistent semantic indexing using **ChromaDB**.
- **Local AI Generation**: Powered by **Ollama** using the `llama3.2:1b` model for privacy and performance.
- **Interactive Chat**: A clean, minimalist interface for querying documents with source citation.
- **Contextual History**: Maintains recent conversation history to provide coherent multi-turn interactions.

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
- **LLM Engine**: [Ollama](https://ollama.com/) (running `llama3.2:1b`)
- **Document Processing**: [PyMuPDF](https://pymupdf.readthedocs.io/) (fitz)
- **Language**: Python 3.10+

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.10+)
- [Ollama](https://ollama.com/) installed and running locally.

### 1. Setup Ollama

Pull the required model:
```bash
ollama pull llama3.2:1b
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

The API will be available at `http://localhost:8000`.

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

Open `http://localhost:5173` in your browser.

---

## 📖 Development Philosophy

- **Educational First**: Prioritize understanding internal mechanics (chunking, embeddings, similarity) over convenience libraries.
- **MVP Focus**: Deliver a working RAG pipeline quickly with a polished UI.
- **Simplicity**: Maintain a clean architecture with minimal abstractions.
- **Privacy**: All processing and AI generation happens locally on your machine.

---

## 🗺️ Project Structure

```text
.
├── backend/
│   ├── app/                # FastAPI application logic
│   │   ├── main.py         # API endpoints and server setup
│   │   └── rag.py          # Core RAG logic (ChromaDB + Ollama)
│   ├── chroma_db/          # Persistent vector database storage
│   ├── uploads/            # Temporary storage for uploaded documents
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.tsx         # Main application component
    │   └── assets/         # Static assets and styles
    └── package.json        # Frontend dependencies
```

---

## 📜 License

This project is for educational purposes. Feel free to explore, learn, and adapt for your own studies.
