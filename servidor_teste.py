"""
Script de Teste Rápido - Sem Integração Completa
Desenvolvido por: Marcio Góes do Nascimento

Este script testa apenas o backend (sem interface)
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uvicorn
from auth import usuario_atual
from rotas_projetos import router as projetos_router

# Criar app
app = FastAPI(
    title="RAG Chatbot API - Sistema de Projetos (TESTE)",
    description="Versão de teste com gestão de projetos",
    version="3.0.0-test"
)

# Incluir rotas de projetos
app.include_router(projetos_router)

# Health check
@app.get("/health")
async def health_check():
    return {
        'status': 'healthy',
        'desenvolvedor': 'Marcio Góes do Nascimento',
        'versao': '3.0.0-test',
        'sistema_projetos': 'ativo'
    }

# Login (simplificado para teste)
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    from auth import autenticar_usuario, criar_token_acesso
    from config_usuarios import ACCESS_TOKEN_EXPIRE_MINUTES
    from datetime import timedelta
    
    usuario = autenticar_usuario(request.username, request.password)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": request.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": request.username,
            "nome": usuario["nome"],
            "email": usuario["email"]
        }
    }

@app.get("/me")
async def get_current_user(current_user: dict = Depends(usuario_atual)):
    return current_user

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SERVIDOR DE TESTE - SISTEMA DE PROJETOS")
    print("   Desenvolvido por: Marcio Góes do Nascimento")
    print("=" * 60)
    print()
    print("📡 Servidor iniciando em: http://localhost:8000")
    print("📖 Documentação API: http://localhost:8000/docs")
    print()
    print("🔐 Credenciais de teste:")
    print("   Admin: admin / Admin@RAG2024!Secure")
    print("   User:  marcio / Marcio@2024!Dev")
    print()
    print("🧪 Para testar, execute em outro terminal:")
    print("   python teste_sistema.py")
    print()
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
