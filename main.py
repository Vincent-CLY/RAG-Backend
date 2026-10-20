import os
from pathlib import Path
from shutil import copyfileobj
import tempfile
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
from langchain_docling.loader import DoclingLoader, ExportType
from docling.chunking import HybridChunker
from langchain_core.documents import Document
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams, PointStruct, Document
from langchain.chat_models import init_chat_model

import uvicorn
from typing import Annotated
from fastapi import FastAPI, File, Form, UploadFile, HTTPException

# ALLOWED_EXTENSIONS = {
#     ".pdf", ".docx", ".doc",
#     ".pptx", ".ppt",
#     ".xlsx", ".xls", ".csv",
#     ".txt", ".md", ".html"
# }

class DocumentCategory(str, Enum):
    RESUME = "resume"
    PROJECT = "project"
    CERTIFICATE = "certificate"
    OTHER = "other"

class UploadFileResponse(BaseModel):
    filename: str
    category: DocumentCategory
    content_type: str | None = None
    file_size: int
    chunks_count: int
    status: str = "success"
    message: str = "File uploaded successfully"

load_dotenv()
EMBED_MODEL_ID = os.getenv("EMBED_MODEL_ID")
# Initialize the embedding model
embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL_ID)

QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
# Initialize the Qdrant client
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    prefer_grpc=True,
    collection_name="my-RAG-collection",
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    vector_name="dense",
    retrieval_mode=RetrievalMode.DENSE,
)

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(
    file: Annotated[UploadFile, File(description="Upload a file")],
    category: Annotated[DocumentCategory, Form(description="Select a document category")]
):
    # CHANGED: BYPASS EXTENSION CHECK FOR ALL FILE TYPES, INCLUDING CODESPACE
    # if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
    #     raise HTTPException(status_code=400, detail="File type not allowed. Please upload a valid file.")

    # CHANGED: MOBILE DEVICES MAY NOT PROVIDE FILE SIZE, SO WE NEED TO CHECK THE CONTENT LENGTH INSTEAD
    # if file.size is not None and file.size == 0:
    #     raise HTTPException(status_code=400, detail="File size is 0KB. Please upload a valid file.")

    received_file = await file.read()
    if len(received_file) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # CHANGED: WINDOWS USES MUTEX WHEN USING WITH TEMPFILE, SO WE NEED TO USE A DIFFERENT APPROACH 
    # with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
    #     tmp_file.write(received_file)
    #     tmp_file_path = tmp_file.name

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
    tmp_file_path = tmp_file.name
    try:
        # ── Stage A：Write to temporary file in disk ──
        try:
            tmp_file.write(received_file)
            tmp_file.flush()  # Ensure all data is written to disk
            tmp_file.close() # Close the file to avoid issues on Windows
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Error writing to temporary file: {str(e)}")

        # ── Stage B：Initialize loader（file not exists/wrong file path）──
        try:
            loader = DoclingLoader(
                file_path=tmp_file_path,
                export_type=ExportType.DOC_CHUNKS,
                chunker=HybridChunker()
            )
        except FileNotFoundError as e:
            raise HTTPException(status_code=400, detail=f"Error recognizing the uploaded file: {str(e)}")

        # ── Stage C：Parse to documents from the temporary file ──
        try:
            docs = loader.load()
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Error parsing the uploaded file: {str(e)}")

    except HTTPException:
        raise  # Re-raise the HTTPException to be handled by FastAPI
    except Exception as e: # Non-HTTP exceptions are unexpected and should be logged for debugging
        raise HTTPException(status_code=500, detail=f"Unexpected error processing the uploaded file: {str(e)}")

    finally:
        Path(tmp_file_path).unlink(missing_ok=True)  # Clean up the temporary file after processing

    DOC_TYPE = "document" # Will change for different document types in the future
    # Inject metatdata into the document
    for doc in docs:
        try:
            doc.metadata["source"] = file.filename           # For referencing the original file
            doc.metadata["category"] = category.value        # For filtering 
            doc.metadata["document_type"] = DOC_TYPE         # For categorization

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving document to Qdrant: {str(e)}")

    # Initialize and Save Qdrant Store using Qdrant Cloud
    try:
        qdrant.add_documents(documents=docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving documents to Qdrant: {str(e)}")


    return UploadFileResponse(
        filename=file.filename,
        category=category,
        content_type=file.content_type,
        file_size=file.size,
        chunks_count=len(docs)
    )
    

# ── Step 3：Retrieve ──────────────────────────────────────────
# QdrantClient vs QdrantVectorStore（一句分清）：
#   QdrantClient      = Qdrant 官方 raw client：講「向量 list + payload dict」，
#                       識建/刪 collection、upsert、scroll raw points（我哋 /tmp 驗證 script 用佢）
#   QdrantVectorStore = LangChain 包裝住 QdrantClient：識 Document、識 Embeddings
#                       （文字↔向量自動轉）、識 filter dict、駁到 chain/agent 做 retriever
# 分工：RAG 讀寫用 VectorStore；管倉（建/刪/驗證）先直接用 QdrantClient。


@app.post("/retrieve")
async def retrieve():
    return {"message": "Retrieve endpoint"}

def main() -> None:
    uvicorn.run(app, host="localhost", port=8000)
    

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    main()