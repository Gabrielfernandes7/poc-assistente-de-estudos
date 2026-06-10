import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
import ollama
from typing import List, Dict, Optional
import os

class RAGManager:
    def __init__(self):
        # Use absolute path for DB
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Default embedding function (sentence-transformers/all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def get_collection(self, notebook_id: str):
        """Get or create a collection for a specific notebook."""
        return self.client.get_or_create_collection(
            name=f"notebook_{notebook_id}",
            embedding_function=self.embedding_function
        )

    def is_indexed(self, notebook_id: str, doc_id: str) -> bool:
        """Check if a document is already in the notebook's vector database."""
        collection = self.get_collection(notebook_id)
        results = collection.get(where={"source": doc_id}, limit=1)
        return results and len(results['ids']) > 0

    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def extract_text_from_md(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def chunk_text(self, text: str, chunk_size: int = 600, chunk_overlap: int = 100) -> List[str]:
        """Split text into chunks with overlap for better context."""
        chunks = []
        if not text: return []
        # Simple character-based chunking (can be improved to word-based)
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks

    def add_to_vector_db(self, notebook_id: str, chunks: List[str], doc_id: str):
        if not chunks: return
        collection = self.get_collection(notebook_id)
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": doc_id} for _ in range(len(chunks))]
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

    def delete_document(self, notebook_id: str, doc_id: str):
        """Remove a document's vectors from the collection."""
        collection = self.get_collection(notebook_id)
        collection.delete(where={"source": doc_id})

    def delete_notebook_collection(self, notebook_id: str):
        """Delete the entire collection for a notebook."""
        try:
            self.client.delete_collection(name=f"notebook_{notebook_id}")
        except:
            pass # Collection might not exist

    def query(self, notebook_id: str, question: str, model: str = "llama3.2:1b", n_results: int = 5) -> Dict:
        collection = self.get_collection(notebook_id)
        
        # Check if collection is empty
        if collection.count() == 0:
            return {"answer": "Este notebook ainda não possui referências. Por favor, faça upload de um arquivo PDF ou Markdown.", "sources": []}

        # Retrieve relevant chunks
        results = collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return {"answer": "Não encontrei informações relevantes nos documentos deste notebook para responder sua pergunta.", "sources": []}

        context = "\n\n---\n\n".join(results['documents'][0])
        sources = list(set([m['source'] for m in results['metadatas'][0]]))
        
        # Refined prompt to reduce hallucinations
        prompt = f"""Você é um assistente de estudos rigoroso e prestativo. Seu objetivo é responder perguntas baseando-se EXCLUSIVAMENTE no contexto fornecido abaixo.

REGRAS CRÍTICAS:
1. Se a resposta não estiver contida no contexto fornecido, diga explicitamente: "Sinto muito, mas não encontrei informações sobre isso nos documentos deste notebook."
2. NÃO utilize conhecimentos externos ou invente fatos.
3. Mantenha a resposta concisa e direta ao ponto.
4. Se houver informações conflitantes, mencione o que cada fonte diz.

CONTEXTO RECUPERADO:
{context}

PERGUNTA DO USUÁRIO: {question}

RESPOSTA:"""
        
        try:
            # Use ollama with low temperature for more factual answers
            response = ollama.generate(
                model=model, 
                prompt=prompt,
                options={
                    "temperature": 0.2, # Lower temperature = less creative, more factual
                }
            )
            
            return {
                "answer": response['response'],
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"Erro ao consultar o modelo {model}: {str(e)}",
                "sources": []
            }

rag_manager = RAGManager()
