import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
import ollama
from typing import List, Dict
import os

class RAGManager:
    def __init__(self, collection_name: str = "book_collection"):
        # Use absolute path for DB to avoid confusion
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Default embedding function (sentence-transformers/all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        self.model = "llama3.2:1b"

    def is_indexed(self, doc_id: str) -> bool:
        """Check if a document is already in the vector database."""
        results = self.collection.get(where={"source": doc_id}, limit=1)
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

    def chunk_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        chunks = []
        if not text: return []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def add_to_vector_db(self, chunks: List[str], doc_id: str):
        if not chunks: return
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": doc_id} for _ in range(len(chunks))]
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

    def query(self, question: str, n_results: int = 2) -> Dict:
        # Check if collection is empty
        if self.collection.count() == 0:
            return {"answer": "No documents uploaded yet. Please upload a PDF or Markdown file first.", "sources": []}

        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return {"answer": "I couldn't find any relevant information in the uploaded documents.", "sources": []}

        context = "\n".join(results['documents'][0])
        sources = list(set([m['source'] for m in results['metadatas'][0]]))
        
        prompt = f"""You are a helpful study assistant. Use the following pieces of retrieved context to answer the question. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer concise.

        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        # Use ollama directly
        response = ollama.generate(model=self.model, prompt=prompt)
        
        return {
            "answer": response['response'],
            "sources": sources
        }

rag_manager = RAGManager()
