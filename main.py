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
QDRANT_URL=os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")


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

    # Initialize the embedding model
    embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL_ID)

    # Initialize and Save Qdrant Store using Qdrant Cloud
    try:
        qdrant = QdrantVectorStore.from_documents(
            docs,
            embeddings,
            url=QDRANT_URL,
            prefer_grpc=True,
            api_key=QDRANT_API_KEY,
            collection_name="my-RAG-collection",
            retrieval_mode=RetrievalMode.DENSE,
            vector_name="dense",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving documents to Qdrant: {str(e)}")


    return UploadFileResponse(
        filename=file.filename,
        category=category,
        content_type=file.content_type,
        file_size=file.size,
        chunks_count=len(docs)
    )
    

class RAGRequest(BaseModel):
    """Deterministic inbound contract for the /query endpoint (V1 foundation)."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question for the RAG pipeline.",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Number of chunks to retrieve (bounded 1-20).",
    )
    category: DocumentCategory | None = Field(
        default=None,
        description="Optional metadata pre-filter (e.g. only search the resume).",
    )


# def save_documents_to_qdrant():
#     loader = DoclingLoader(
#         file_path="path",
#         export_type="",
#         chunker=HybridChunker(chunk_size=500, chunk_overlap=50)
#     )
#     docs = loader.load()

def main() -> None:
    request = RAGRequest(question="What is RAG?", top_k=3)
    print("Valid request  ->", request.model_dump())

    # Pydantic acts as a strict border guard: out-of-range values are rejected
    # BEFORE any expensive retrieval or LLM call is ever made.
    try:
        bad_request = RAGRequest(question="What is RAG?", top_k=99)
        print("This line is never reached ->", bad_request)
    except ValidationError as exc:
        print("Rejected bad request (top_k=99 out of range):")
        print(exc)

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    main()