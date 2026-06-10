import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.rag import rag_manager

app = FastAPI(title="BookSelfStudy API")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
HISTORY_FILE = os.path.join(os.path.dirname(BASE_DIR), "chat_history.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

@app.get("/")
async def root():
    return {"message": "BookSelfStudy Backend is running"}

@app.get("/history")
async def get_history():
    return load_history()

@app.delete("/history")
async def clear_history():
    save_history([])
    return {"message": "History cleared"}

@app.get("/files")
async def list_files():
    try:
        if not os.path.exists(UPLOAD_DIR):
            return {"files": []}
        files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
        return {"files": files}
    except Exception as e:
        print(f"Error listing files: {e}")
        return {"files": []}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.md')):
        raise HTTPException(status_code=400, detail="Only PDF and Markdown files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Check if already indexed (Cache check)
        if rag_manager.is_indexed(file.filename):
            return {"message": f"{file.filename} already indexed.", "status": "cached"}

        if file.filename.endswith('.pdf'):
            text = rag_manager.extract_text_from_pdf(file_path)
        else:
            text = rag_manager.extract_text_from_md(file_path)
            
        chunks = rag_manager.chunk_text(text)
        rag_manager.add_to_vector_db(chunks, file.filename)
        
        return {"message": f"Successfully processed {file.filename}", "chunks_count": len(chunks)}
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    try:
        # This might be slow depending on the model and hardware
        result = rag_manager.query(request.question)
        
        # Save to history
        history = load_history()
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": result["answer"], "sources": result["sources"]})
        save_history(history[-20:]) # Keep only last 20 messages for performance
        
        return result
    except Exception as e:
        print(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
