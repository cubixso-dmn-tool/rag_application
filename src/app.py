import os
import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import tempfile
import shutil
from ingest import Ingestor
from rag import answer_question

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
KNOWLEDGE_BASE_FOLDER = os.path.join(PROJECT_ROOT, "knowledge_base")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWLEDGE_BASE_FOLDER, exist_ok=True)

class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    message: str

class ChatResponse(BaseModel):
    response: str
    message: str

class IngestResponse(BaseModel):
    message: str
    files_processed: int

global_ingestor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global global_ingestor
    global_ingestor = Ingestor()
    if os.listdir(KNOWLEDGE_BASE_FOLDER):
        global_ingestor.ingest_folder(KNOWLEDGE_BASE_FOLDER)
        global_ingestor.build_index()
        print("Initialized with existing knowledge base")
    yield
    global_ingestor = None

app = FastAPI(
    title="RAG Application API",
    description="A REST API for document ingestion and question answering using RAG",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RAG Application API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ingestor_ready": global_ingestor is not None}

@app.post("/ingest/folder")
async def ingest_folder_endpoint():
    global global_ingestor
    try:
        if not global_ingestor:
            global_ingestor = Ingestor()
        
        files_before = len(global_ingestor.documents)
        global_ingestor.ingest_folder(KNOWLEDGE_BASE_FOLDER)
        global_ingestor.build_index()
        files_processed = len(global_ingestor.documents) - files_before
        
        return IngestResponse(
            message="Successfully ingested documents from knowledge base folder",
            files_processed=files_processed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting folder: {str(e)}")

@app.post("/ingest/upload")
async def upload_and_ingest(file: UploadFile = File(...)):
    global global_ingestor
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = {'.pdf', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}")
    
    try:
        if not global_ingestor:
            global_ingestor = Ingestor()
        
        temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        files_before = len(global_ingestor.documents)
        
        if file_ext == '.pdf':
            global_ingestor.ingest_pdf(temp_path, meta={'type': 'uploaded'})
        elif file_ext == '.txt':
            global_ingestor.ingest_txt(temp_path, meta={'type': 'uploaded'})
        
        global_ingestor.build_index()
        files_processed = len(global_ingestor.documents) - files_before
        
        return IngestResponse(
            message=f"Successfully uploaded and ingested {file.filename}",
            files_processed=files_processed
        )
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/query")
async def query_documents(request: QueryRequest):
    global global_ingestor
    
    if not global_ingestor or not global_ingestor.index:
        raise HTTPException(status_code=400, detail="No documents have been ingested yet. Please ingest documents first.")
    
    try:
        answer = answer_question(global_ingestor, request.question, k=request.k)
        return QueryResponse(
            answer=answer,
            message="Query processed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/status")
async def get_status():
    global global_ingestor
    
    if not global_ingestor:
        return {
            "ingestor_initialized": False,
            "documents_count": 0,
            "index_built": False
        }
    
    return {
        "ingestor_initialized": True,
        "documents_count": len(global_ingestor.documents),
        "index_built": global_ingestor.index is not None
    }

@app.delete("/reset")
async def reset_ingestor():
    global global_ingestor
    global_ingestor = Ingestor()
    return {"message": "Ingestor has been reset"}

@app.post("/chat")
async def chat_with_documents(
    question: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Process files on-demand and answer questions without storing documents
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if not question.strip():
        raise HTTPException(status_code=400, detail="No question provided")
    
    # Create a temporary ingestor for this request
    temp_ingestor = Ingestor()
    temp_files = []
    
    try:
        # Process each uploaded file
        for file in files:
            if not file.filename:
                continue
                
            allowed_extensions = {'.pdf', '.txt'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
                )
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            temp_files.append(temp_file.name)
            
            # Save uploaded content to temp file
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Ingest the temporary file
            if file_ext == '.pdf':
                temp_ingestor.ingest_pdf(temp_file.name, meta={'type': 'temp', 'filename': file.filename})
            elif file_ext == '.txt':
                temp_ingestor.ingest_txt(temp_file.name, meta={'type': 'temp', 'filename': file.filename})
        
        # Build index for this session
        temp_ingestor.build_index()
        
        # Answer the question
        if not temp_ingestor.index:
            raise HTTPException(status_code=500, detail="Failed to build index from uploaded files")
        
        answer = answer_question(temp_ingestor, question, k=5)
        
        return ChatResponse(
            response=answer,
            message="Question answered successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as cleanup_error:
                print(f"Error cleaning up temp file {temp_file_path}: {cleanup_error}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)