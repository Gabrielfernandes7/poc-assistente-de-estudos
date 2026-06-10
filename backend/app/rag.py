import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
import ollama
from typing import List, Dict, Optional
import os
import re
import uuid
import logging
import pytesseract
from PIL import Image
import io
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self):
        # Configuração de Persistência (Modo Local vs Modo Servidor)
        # Se as variáveis de ambiente estiverem presentes, conecta ao servidor remoto (ex: produção)
        # Caso contrário, usa o banco local persistente.
        host = os.getenv("CHROMA_HOST")
        port = os.getenv("CHROMA_PORT")
        
        if host and port:
            logger.info(f"Conectando ao servidor ChromaDB em {host}:{port}")
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
            logger.info(f"Usando ChromaDB Local em {db_path}")
            self.client = chromadb.PersistentClient(path=db_path)
        
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def get_collection(self, notebook_id: str):
        """Get or create a collection for a specific notebook."""
        clean_id = notebook_id.replace("-", "")
        return self.client.get_or_create_collection(
            name=f"nb_{clean_id}",
            embedding_function=self.embedding_function
        )

    def is_indexed(self, notebook_id: str, doc_id: str) -> bool:
        """Check if a document is already in the notebook's vector database."""
        try:
            collection = self.get_collection(notebook_id)
            results = collection.get(where={"source": doc_id}, limit=1)
            return results and len(results['ids']) > 0
        except Exception as e:
            logger.error(f"Error checking index for {doc_id}: {e}")
            return False

    def extract_text_from_pdf(self, file_path: str) -> List[Dict]:
        """Extrai texto e metadados (página) do PDF, com fallback para OCR."""
        pages_content = []
        try:
            with fitz.open(file_path) as doc:
                for page_num, page in enumerate(doc):
                    text = page.get_text("text").strip()
                    
                    # Heurística de OCR: Se a página tem pouquíssimo texto, pode ser um scan
                    # Documentos jurídicos costumam ter ao menos 50 caracteres por página
                    if len(text) < 50:
                        logger.info(f"Página {page_num + 1} parece ser uma imagem. Iniciando OCR...")
                        ocr_text = self._run_ocr_on_page(page)
                        if ocr_text:
                            text = ocr_text
                    
                    if text:
                        text = re.sub(r'\s+', ' ', text).strip()
                        pages_content.append({
                            "text": text,
                            "page": page_num + 1
                        })
            return pages_content
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return []

    def _run_ocr_on_page(self, page) -> str:
        """Converte a página do PDF em imagem e executa o Tesseract."""
        try:
            # Renderiza a página como imagem (pixmap)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Aumenta a resolução para 2x (melhora OCR)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Executa OCR (configurado para Português e Inglês)
            # Nota: Requer tesseract-ocr instalado no sistema (sudo apt install tesseract-ocr)
            text = pytesseract.image_to_string(img, lang='por+eng')
            return text.strip()
        except Exception as e:
            logger.error(f"Falha no OCR da página: {e}")
            return ""

    def extract_text_from_md(self, file_path: str) -> List[Dict]:
        """Extrai texto de Markdown."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [{"text": f.read(), "page": 1}]
        except Exception as e:
            logger.error(f"Error reading MD {file_path}: {e}")
            return []

    def chunk_content(self, pages_content: List[Dict], chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Divide o conteúdo em chunks mantendo metadados de origem.
        Implementação inspirada em RecursiveCharacterTextSplitter.
        """
        chunks = []
        for item in pages_content:
            text = item["text"]
            page = item["page"]
            
            if len(text) <= chunk_size:
                chunks.append({"text": text, "page": page})
                continue
            
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end]
                chunks.append({"text": chunk_text, "page": page})
                start += chunk_size - overlap
                if end >= len(text):
                    break
                    
        return chunks

    def add_to_vector_db(self, notebook_id: str, chunks: List[Dict], doc_id: str):
        if not chunks:
            return
        try:
            collection = self.get_collection(notebook_id)
            
            documents = [c["text"] for c in chunks]
            metadatas = [{"source": doc_id, "page": c["page"]} for c in chunks]
            ids = [f"{doc_id}_{i}_{uuid.uuid4().hex[:6]}" for i in range(len(chunks))]
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"SUCCESS: Indexed {len(chunks)} chunks for {doc_id}.")
        except Exception as e:
            logger.error(f"CRITICAL ERROR adding to vector DB: {e}")
            raise e

    def delete_document(self, notebook_id: str, doc_id: str):
        try:
            collection = self.get_collection(notebook_id)
            collection.delete(where={"source": doc_id})
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")

    def delete_notebook_collection(self, notebook_id: str):
        clean_id = notebook_id.replace("-", "")
        try:
            self.client.delete_collection(name=f"nb_{clean_id}")
        except Exception as e:
            logger.debug(f"Collection not found for deletion: {e}")

    def query(self, notebook_id: str, question: str, model: str = "llama3.2:1b", n_results: int = 5) -> Dict:
        try:
            collection = self.get_collection(notebook_id)
            
            count = collection.count()
            if count == 0:
                return {
                    "answer": "Este notebook parece não ter documentos indexados no momento. Por favor, faça o upload de uma referência.", 
                    "sources": []
                }

            # Busca semântica
            results = collection.query(
                query_texts=[question],
                n_results=min(n_results, count)
            )
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    "answer": "Não encontrei informações relevantes nos documentos para responder sua pergunta.", 
                    "sources": []
                }

            context_parts = []
            sources_with_pages = []
            
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                source_info = f"{meta['source']} (pág. {meta['page']})"
                sources_with_pages.append(source_info)
                context_parts.append(f"--- TRECHO DE {source_info} ---\n{doc}")
            
            context = "\n\n".join(context_parts)
            
            prompt = f"""Você é um Assistente Jurídico e de Estudos altamente preciso.
Sua tarefa é responder à pergunta baseando-se EXCLUSIVAMENTE no contexto fornecido.

REGRAS CRÍTICAS:
1. Cite sempre o nome do arquivo e a página ao usar uma informação (ex: [Nome do Arquivo, pág. X]).
2. Se a informação não estiver no contexto, responda honestamente que não sabe.
3. Não use conhecimento externo. Use apenas o que foi fornecido.
4. Mantenha um tom profissional e direto.

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA (Em Português):"""
            
            response = ollama.generate(
                model=model, 
                prompt=prompt,
                options={"temperature": 0, "num_ctx": 4096} # Temp 0 para maior fidelidade
            )
            
            return {
                "answer": response['response'],
                "sources": list(set(sources_with_pages))
            }
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "answer": f"Erro técnico: {str(e)}",
                "sources": []
            }

rag_manager = RAGManager()
