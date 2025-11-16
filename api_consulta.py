"""
API de Consulta RAG - Independente
Use esta API para consultar documentos de qualquer chatbot externo
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from rag_engine import RAGEngine

# API simples e independente
app = FastAPI(
    title="API de Consulta RAG",
    description="Consulte documentos processados de qualquer chatbot",
    version="1.0.0"
)

# Inicializa o RAG Engine
rag_engine = RAGEngine(persist_directory="./chroma_db")

# Modelos
class SearchRequest(BaseModel):
    query: str
    n_results: int = 3
    
class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int

# Endpoints

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Busca documentos relevantes
    
    Exemplo de uso:
    ```
    POST http://localhost:8001/search
    {
        "query": "qual o conteúdo do documento X?",
        "n_results": 3
    }
    ```
    """
    try:
        results = rag_engine.search(
            query=request.query,
            n_results=request.n_results
        )
        
        return {
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Retorna estatísticas do banco de dados"""
    return rag_engine.get_stats()

@app.get("/documents")
async def list_documents():
    """Lista todos os documentos disponíveis"""
    return rag_engine.list_documents()

@app.get("/health")
async def health_check():
    """Verifica status da API"""
    return {
        "status": "operational",
        "database": "connected",
        "total_documents": len(rag_engine.list_documents())
    }

if __name__ == "__main__":
    print("🔍 API de Consulta RAG Iniciada!")
    print("📡 Acesse: http://localhost:8001")
    print("\n📋 Documentação: http://localhost:8001/docs")
    print("\n💡 Exemplo de uso:")
    print('   curl -X POST "http://localhost:8001/search" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"query": "sua pergunta", "n_results": 3}\'')
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
