# src/main.py
from fastapi import FastAPI, Query, HTTPException
from api.routes import router
from services.RAG_service import RAGService
from config.settings import settings
from services.document_store import QdrantDocumentStore
app = FastAPI(
    title="Qdrant Document Search System",
    description="A sophisticated document search and management system using Qdrant vector database",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


doc_store = QdrantDocumentStore()
rag_service = RAGService(doc_store)
# تضمين routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Document Search System & RAG",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.post("/ask")
async def ask_qusetion(
    query: str = Query(..., description= "Your Answer"),
    limit: int = Query(5)):
    
    try:
        result = rag_service.ask_question(query, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)