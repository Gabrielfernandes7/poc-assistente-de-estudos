# BookSelfStudy: Project Context & Status

BookSelfStudy é um projeto de estudo pessoal criado para aprender e dominar o ciclo de vida de **Retrieval-Augmented Generation (RAG)**.

## 🎯 Objetivo
Entender as mecânicas internas de ingestão, fragmentação (chunking), embeddings, busca semântica e integração com LLMs locais, priorizando o aprendizado prático sobre abstrações prontas.

## 🏗️ Estado Atual da Implementação

### Pipeline RAG
- [x] **Ingestão**: Suporte a PDF e Markdown.
- [x] **OCR**: Implementado com Tesseract para suporte a PDFs escaneados.
- [x] **Chunking**: Fragmentação recursiva de caracteres (1000/200).
- [x] **Embeddings**: ChromaDB Default.
- [x] **Vector Storage**: ChromaDB (Persistente local).
- [x] **Retrieval**: Busca semântica por notebook-id.
- [x] **Generation**: Integração com Ollama (Llama 3.2, Qwen).
- [x] **Citações**: Fonte e página retornadas na resposta.

### Backend (Python/FastAPI)
- [x] API de gestão de Notebooks.
- [x] Processamento de arquivos em Background.
- [x] Histórico de chat persistente por notebook.
- [x] Seleção dinâmica de modelos Ollama.

### Frontend (React/Vite)
- [x] Interface moderna inspirada no NotebookLM.
- [x] Gestão de múltiplos notebooks.
- [x] Visualização de referências e status de indexação.
- [x] Chat interativo com referências.

## 🛠️ Stack Tecnológica
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS 4.
- **Backend:** Python 3.10, FastAPI, ChromaDB.
- **IA Local:** Ollama.
- **Bibliotecas Chave:** PyMuPDF, Pytesseract, Axios, Lucide-React.

## 🎨 Diretrizes de UI/UX
- **Tema:** Estética "limpa e branca para estudos".
- **Interações:** Feedback visual de processamento e fontes clicáveis.
- **Foco:** Minimalismo e clareza no conteúdo.

## 📜 Filosofia de Desenvolvimento
- **Educacional Primeiro:** Entender o porquê antes do como.
- **Local-First:** Privacidade e controle total sobre os dados e modelos.
- **Simplicidade:** Evitar over-engineering (como Auth/Multi-tenancy) para focar na lógica do RAG.

---
*This file serves as the foundational context for Gemini CLI. Adhere to these principles and the project scope in all subsequent tasks.*
