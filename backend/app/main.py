import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app.rag import rag_manager
from app.metadata import metadata_manager

app = FastAPI(title="BookSelfStudy API")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
HISTORY_FILE = os.path.join(os.path.dirname(BASE_DIR), "chat_history.json")

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

# --- File Endpoints ---

@app.get("/notebooks/{notebook_id}/files")
async def list_files(notebook_id: str):
    upload_dir = get_notebook_upload_dir(notebook_id)
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    return {"files": files}

@app.post("/notebooks/{notebook_id}/upload")
async def upload_document(notebook_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.md')):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF e Markdown são suportados.")
    
    upload_dir = get_notebook_upload_dir(notebook_id)
    file_path = os.path.join(upload_dir, file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Check if already indexed (Cache check)
        if rag_manager.is_indexed(notebook_id, file.filename):
            return {"message": f"{file.filename} já indexado.", "status": "cached"}

        if file.filename.endswith('.pdf'):
            text = rag_manager.extract_text_from_pdf(file_path)
        else:
            text = rag_manager.extract_text_from_md(file_path)
            
        chunks = rag_manager.chunk_text(text)
        rag_manager.add_to_vector_db(notebook_id, chunks, file.filename)
        
        return {"message": f"Sucesso ao processar {file.filename}", "chunks_count": len(chunks)}
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notebooks/{notebook_id}/files/{filename}")
async def delete_file(notebook_id: str, filename: str):
    # 1. Delete from vector db
    rag_manager.delete_document(notebook_id, filename)
    
    # 2. Delete physical file
    upload_dir = get_notebook_upload_dir(notebook_id)
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return {"message": f"Arquivo {filename} removido com sucesso"}

# --- Query Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    try:
        # Update last used model in metadata
        metadata_manager.update_model(request.notebook_id, request.model)
        
        result = rag_manager.query(request.notebook_id, request.question, model=request.model)
        return result
    except Exception as e:
        print(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "BookSelfStudy API is running with Notebook support"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
