# BookSelfStudy: Project Context & Instructions

BookSelfStudy is a personal study project created to learn and understand **Retrieval-Augmented Generation (RAG)** by building a complete application from scratch. It is inspired by Google NotebookLM but focuses on educational simplicity.

## 🎯 Main Goal
The primary objective is to learn the entire RAG development lifecycle end-to-end. This includes document ingestion, text extraction, chunking, embeddings, vector storage, semantic search, and LLM integration. The focus is on understanding internal mechanics rather than relying on black-box abstractions.

## 🏗️ Application Overview
BookSelfStudy is a document-based chatbot. Users upload PDF or Markdown files and interact with them through a chat interface. The assistant provides answers grounded in the uploaded content, including source citations.

### User Flow
1. **Upload:** User provides a PDF or Markdown file.
2. **Process:** Extract text and split into manageable chunks.
3. **Embed:** Generate vector embeddings for each chunk.
4. **Store:** Save embeddings in a vector database (e.g., ChromaDB).
5. **Query:** User asks a question.
6. **Retrieve:** Find the most relevant chunks via semantic search.
7. **Generate:** LLM produces an answer using the retrieved context.
8. **Respond:** Return answer with supporting sources.

## 🛠️ Technical Stack (Suggested)
- **Frontend:** React + Vite + TypeScript.
- **Backend:** Python + FastAPI.
- **RAG Logic:** Custom implementation or LangChain.
- **Models:** Ollama (Llama 3.2, Qwen) or llama.cpp for local execution.
- **Vector DB:** ChromaDB or FAISS.
- **Document Processing:** PyMuPDF (PDF), Native Markdown parsing.

## 🎨 UI/UX Guidelines
- **Theme:** Clean, "white for studies" aesthetic (NotebookLM-style).
- **Interactions:** Use hover effects with specific colors: Green, Red, Blue, and Yellow.
- **Layout:** Minimalist and focused on the document/chat interaction.

## 📜 Development Philosophy
- **Educational First:** Prioritize understanding over convenience.
- **MVP Focus:** Deliver working software quickly.
- **Simplicity:** Prefer readability and simple architecture over clever abstractions.
- **No Over-engineering:** Avoid enterprise features (Auth, Multi-tenancy, Billing) to keep the focus on the RAG pipeline.

## 🚀 Getting Started (TODO)
*Note: This section should be updated once the project structure is initialized.*

### Frontend
- **Install:** `npm install`
- **Run:** `npm run dev`

### Backend
- **Setup:** `cd backend && virtualenv venv && ./venv/bin/pip install -r requirements.txt`
- **Run:** `./venv/bin/python3 -m uvicorn app.main:app --reload`

---
*This file serves as the foundational context for Gemini CLI. Adhere to these principles and the project scope in all subsequent tasks.*
