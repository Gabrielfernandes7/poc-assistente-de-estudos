# BookSelfStudy 📚

BookSelfStudy é uma plataforma educacional desenvolvida para explorar e entender a mecânica interna de **Retrieval-Augmented Generation (RAG)**. Inspirado no Google NotebookLM, ele permite que os usuários façam upload de documentos e interajam com eles através de um assistente de IA fundamentado (grounded).

Este projeto é uma iniciativa de estudo pessoal focada na implementação de todo o ciclo de vida do RAG — desde a ingestão de documentos até a busca semântica e geração local com LLMs — sem depender de abstrações de alto nível.

---

## 🏗️ Implementação e Arquitetura

O projeto é dividido em uma arquitetura cliente-servidor, focada em isolamento de contexto (Notebooks) e processamento local.

### 🧠 Pipeline RAG (Retrieval-Augmented Generation)

1.  **Ingestão e Extração**:
    *   **PDF**: Utiliza `PyMuPDF` para extração de texto.
    *   **OCR Fallback**: Se uma página de PDF contém pouco texto (indicando um documento escaneado), o sistema utiliza automaticamente `Tesseract OCR` para extrair o conteúdo.
    *   **Markdown**: Extração direta de texto.
2.  **Fragmentação (Chunking)**:
    *   Os textos são divididos em chunks de ~1000 caracteres com 200 caracteres de sobreposição (overlap) para manter o contexto semântico entre fragmentos.
3.  **Vetorização e Armazenamento**:
    *   Utiliza o **ChromaDB** para armazenar os embeddings e metadados (como nome do arquivo e página).
    *   Cada "Notebook" possui sua própria coleção isolada no banco vetorial.
4.  **Recuperação e Geração**:
    *   Busca semântica recupera os 5 fragmentos mais relevantes.
    *   O contexto é injetado em um prompt estruturado para o **Ollama**.
    *   **Grounding**: O assistente é instruído a responder apenas com base no contexto e a citar as fontes (arquivo e página).

### 🖥️ Backend (FastAPI)

*   **Processamento Assíncrono**: O upload de arquivos inicia uma `Background Task` para processamento e indexação, permitindo que a UI continue responsiva.
*   **Gestão de Metadados**: Um registro JSON persistente (`notebooks_metadata.json`) gerencia o histórico de chat, status de processamento de arquivos e configurações de cada notebook.
*   **Local-First**: Projetado para rodar inteiramente no hardware do usuário.

### 🎨 Frontend (React)

*   **Interface Reativa**: Desenvolvida com React 19 e Vite para máxima performance.
*   **Estilização Moderna**: Utiliza Tailwind CSS 4 para um design limpo e focado em leitura.
*   **Gerenciamento de Estado**: Interface consciente do estado de processamento dos arquivos em tempo real.

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Linguagem**: [Python 3.10+](https://www.python.org/)
- **Framework API**: [FastAPI](https://fastapi.tiangolo.com/)
- **Banco Vetorial**: [ChromaDB](https://www.trychroma.com/)
- **LLM Engine**: [Ollama](https://ollama.com/)
- **Processamento de PDF**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **OCR**: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) & [Pillow](https://python-pillow.org/)

### Frontend
- **Framework**: [React 19](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
- **Ícones**: [Lucide React](https://lucide.dev/)
- **Comunicação**: [Axios](https://axios-http.com/)

---

## 🧪 Ferramentas Avançadas

### Ingest Expert (Destilação de Documentos)
O projeto inclui um script especializado (`backend/ingest_expert.py`) para "destilar" documentos. Ele utiliza o LLM para ler cada página e criar resumos técnicos densos, salvando-os de volta no banco vetorial. Isso melhora a precisão do RAG e economiza tokens.

**Como usar**:
```bash
cd backend
python ingest_expert.py <notebook_id> [modelo]
# Exemplo: python ingest_expert.py 123-abc llama3.2:3b
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

1.  **Ollama**: [Instale o Ollama](https://ollama.com/) e baixe os modelos desejados:
    ```bash
    ollama pull llama3.2:1b
    ollama pull qwen2.5:1.5b
    ```
2.  **Tesseract OCR** (Opcional, para suporte a PDFs escaneados):
    *   Linux: `sudo apt install tesseract-ocr`
    *   macOS: `brew install tesseract`
    *   Windows: Instalar via [binário](https://github.com/UB-Mannheim/tesseract/wiki).
3.  **Node.js v18+** e **Python 3.10+**.

### 1. Configuração do Backend

1.  Navegue até a pasta `backend`:
    ```bash
    cd backend
    ```
2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Inicie o servidor:
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    O servidor estará disponível em `http://localhost:8000`.

### 2. Configuração do Frontend

1.  Navegue até a pasta `frontend`:
    ```bash
    cd frontend
    ```
2.  Instale as dependências:
    ```bash
    npm install
    ```
3.  Inicie o servidor de desenvolvimento:
    ```bash
    npm run dev
    ```
    Acesse `http://localhost:5173` no seu navegador.

---

## 📜 Licença

Este projeto é estritamente para fins educacionais. Sinta-se à vontade para explorar e adaptar para seus próprios estudos.
