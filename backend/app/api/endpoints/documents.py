import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.agents.scholar import ScholarAgent

router = APIRouter()
scholar_agent = ScholarAgent()

# Best Practice: Use absolute paths tied to the file's location to prevent CWD mismatches
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "data", "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

@router.post("/ingest")
def ingest_documents():
    """Manually ingest documents currently in the directory."""
    scholar_agent.ingest_documents(DOCUMENTS_DIR)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = BackgroundTasks() # While valid, usually just `background_tasks: BackgroundTasks` is enough.
):
    """Uploads a PDF and triggers ingestion in the background."""
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}
         
    try:
        # 1. Read the incoming file content BEFORE opening the destination file
        content = await file.read()
        
        # 2. Open the destination file using a DIFFERENT variable name (f or out_file)
        file_path = os.path.join(DOCUMENTS_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
            
        # 3. Queue the ingestion task
        # It's cleaner to reference the agent's function directly rather than the route function
        background_tasks.add_task(scholar_agent.ingest_documents, DOCUMENTS_DIR)
        
        return {"message": f"Document {file.filename} uploaded successfully. Ingestion queued."}
    except Exception as e:
        return {"error": str(e)}
    
       