import os
import json
import shutil
import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import ollama
from app.rag import rag_manager
from app.metadata import metadata_manager

app = FastAPI(title="BookSelfStudy API")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")

os.makedirs(ROOT_UPLOAD_DIR, exist_ok=True)

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    notebook_id: str
    question: str
    model: Optional[str] = "llama3.2:1b"

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

class NotebookCreate(BaseModel):
    name: str

def get_notebook_upload_dir(notebook_id: str):
    path = os.path.join(ROOT_UPLOAD_DIR, notebook_id)
    os.makedirs(path, exist_ok=True)
    return path

def calculate_file_hash(file_path: str) -> str:
    """Calcula o SHA256 do arquivo para identificação única."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def process_document_background(notebook_id: str, file_path: str, filename: str, file_hash: str):
    """Processa o documento em background para não travar o upload."""
    try:
        metadata_manager.update_file_status(notebook_id, filename, "processing")
        
        if filename.endswith('.pdf'):
            content = rag_manager.extract_text_from_pdf(file_path)
        else:
            content = rag_manager.extract_text_from_md(file_path)
            
        chunks = rag_manager.chunk_content(content)
        rag_manager.add_to_vector_db(notebook_id, chunks, filename)
        
        metadata_manager.update_file_status(notebook_id, filename, "ready")
        print(f"Background Process: Sucesso ao indexar {filename}")
    except Exception as e:
        metadata_manager.update_file_status(notebook_id, filename, "error")
        print(f"Background Process Error: {e}")

# --- Notebook Endpoints ---

@app.get("/notebooks")
async def list_notebooks():
    return metadata_manager.load_all()

@app.post("/notebooks")
async def create_notebook(data: NotebookCreate):
    return metadata_manager.create_notebook(data.name)

@app.delete("/notebooks/{notebook_id}")
async def delete_notebook(notebook_id: str):
    # 1. Delete vectors
    rag_manager.delete_notebook_collection(notebook_id)
    
    # 2. Delete files
    upload_dir = os.path.join(ROOT_UPLOAD_DIR, notebook_id)
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    
    # 3. Delete metadata
    success = metadata_manager.delete_notebook(notebook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notebook not found")
        
    return {"message": "Notebook deleted successfully"}

@app.get("/models")
async def list_models():
    """Lista modelos disponíveis no Ollama local."""
    try:
        models_info = ollama.list()
        if isinstance(models_info, dict) and 'models' in models_info:
            return [m['name'] for m in models_info['models']]
        elif hasattr(models_info, 'models'):
            return [m.model for m in models_info.models]
        return ["llama3.2:1b", "qwen2.5:1.5b"]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return ["llama3.2:1b", "qwen2.5:1.5b"]

# --- File Endpoints ---

@app.get("/notebooks/{notebook_id}/files/status")
async def get_files_status(notebook_id: str):
    return metadata_manager.get_files_status(notebook_id)

@app.get("/notebooks/{notebook_id}/files")
async def list_files(notebook_id: str):
    upload_dir = get_notebook_upload_dir(notebook_id)
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    return {"files": files}

@app.post("/notebooks/{notebook_id}/upload")
async def upload_document(notebook_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.md')):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF e Markdown são suportados.")
    
    upload_dir = get_notebook_upload_dir(notebook_id)
    file_path = os.path.join(upload_dir, file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_hash = calculate_file_hash(file_path)
    
    try:
        # Check if already indexed
        if rag_manager.is_indexed(notebook_id, file.filename):
            return {"message": f"{file.filename} já indexado.", "status": "cached"}

        # Adiciona o processamento pesado para rodar em background
        background_tasks.add_task(process_document_background, notebook_id, file_path, file.filename, file_hash)
        
        return {
            "message": f"Arquivo {file.filename} recebido. O processamento iniciou em segundo plano.",
            "status": "processing",
            "hash": file_hash
        }
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notebooks/{notebook_id}/files/{filename}")
async def delete_file(notebook_id: str, filename: str):
    rag_manager.delete_document(notebook_id, filename)
    upload_dir = get_notebook_upload_dir(notebook_id)
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"message": f"Arquivo {filename} removido"}

# --- Query Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    try:
        # Add user message to history
        metadata_manager.add_history_message(request.notebook_id, "user", request.question)
        
        # Update last used model
        metadata_manager.update_model(request.notebook_id, request.model)
        
        result = rag_manager.query(request.notebook_id, request.question, model=request.model)
        
        # Add assistant message to history
        metadata_manager.add_history_message(
            request.notebook_id, 
            "assistant", 
            result["answer"], 
            result["sources"],
            model=request.model
        )
        
        return result
    except Exception as e:
        print(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.delete("/notebooks/{notebook_id}/history")
async def clear_notebook_history(notebook_id: str):
    metadata_manager.clear_history(notebook_id)
    return {"message": "Histórico limpo"}

@app.get("/")
async def root():
    return {"message": "BookSelfStudy API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
