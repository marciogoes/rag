from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
import json
import csv
from pathlib import Path
from datetime import timedelta
import uvicorn
from pydantic import BaseModel

from document_processor import DocumentProcessor
from rag_engine import RAGEngine
from chatbot import RAGChatbot
from auth import autenticar_usuario, criar_token_acesso, usuario_atual
from config_usuarios import ACCESS_TOKEN_EXPIRE_MINUTES

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="RAG Chatbot API - Desenvolvido por Marcio Góes do Nascimento",
    description="Sistema RAG com Claude e autenticação",
    version="2.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR = Path("./exports")
EXPORT_DIR.mkdir(exist_ok=True)

# Inicializa componentes
document_processor = DocumentProcessor()
rag_engine = RAGEngine(persist_directory="./chroma_db")
chatbot = RAGChatbot(rag_engine=rag_engine, llm_provider="anthropic")

# Modelos Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    n_context_docs: int = 3

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    context_used: int
    rag_enabled: bool

# Rotas de Autenticação

@app.post("/login")
async def login(request: LoginRequest):
    """Endpoint de login"""
    usuario = autenticar_usuario(request.username, request.password)
    
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos"
        )
    
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
    """Retorna informações do usuário logado"""
    return current_user

# Rotas Principais

@app.get("/", response_class=HTMLResponse)
async def home():
    """Retorna a interface web com autenticação"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RAG Chatbot - Sistema de IA com Documentos</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.1em; opacity: 0.9; }
            .developer-credit {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
                font-size: 0.9em;
            }
            .developer-credit strong { font-size: 1.1em; }
            
            /* Login Screen */
            .login-container {
                max-width: 400px;
                margin: 100px auto;
                padding: 40px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }
            .login-container h2 {
                color: #667eea;
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                color: #333;
                font-weight: 500;
            }
            .form-group input {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1em;
            }
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
            }
            
            /* Main App */
            #app { display: none; }
            .main-content {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 20px;
                padding: 30px;
            }
            .sidebar {
                border-right: 2px solid #eee;
                padding-right: 20px;
            }
            .user-info {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .user-info .name {
                font-weight: bold;
                color: #667eea;
            }
            .section {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .section h2 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 10px;
                padding: 30px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }
            .upload-area:hover {
                background: #f0f0ff;
                border-color: #764ba2;
            }
            .upload-area.dragover {
                background: #e0e0ff;
                border-color: #764ba2;
            }
            input[type="file"] { display: none; }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                transition: transform 0.2s;
                width: 100%;
                margin-top: 10px;
            }
            .btn:hover { transform: scale(1.05); }
            .btn:active { transform: scale(0.95); }
            .btn-danger {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }
            .btn-success {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            }
            .btn-warning {
                background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            }
            #documentList {
                list-style: none;
                margin-top: 10px;
            }
            #documentList li {
                background: white;
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .chat-container {
                display: flex;
                flex-direction: column;
                height: 600px;
            }
            #chatMessages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .message {
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 10px;
                max-width: 80%;
                animation: slideIn 0.3s ease;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .message.user {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
            }
            .message.bot {
                background: white;
                border: 2px solid #eee;
            }
            .message.bot .sources {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #eee;
                font-size: 0.9em;
                color: #666;
            }
            .chat-input-area {
                display: flex;
                gap: 10px;
            }
            #chatInput {
                flex: 1;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 1em;
            }
            #chatInput:focus {
                outline: none;
                border-color: #667eea;
            }
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 10px;
            }
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .stat-card .value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .stat-card .label {
                color: #666;
                font-size: 0.9em;
                margin-top: 5px;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .loading.active { display: block; }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .export-buttons {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 10px;
            }
            .footer {
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                border-top: 2px solid #eee;
                color: #666;
            }
            .footer strong { color: #667eea; }
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                .sidebar { border-right: none; padding-right: 0; }
            }
        </style>
    </head>
    <body>
        <!-- Login Screen -->
        <div id="loginScreen" class="login-container">
            <h2>🔐 Login - RAG Chatbot</h2>
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label>Usuário:</label>
                    <input type="text" id="username" required placeholder="Digite seu usuário">
                </div>
                <div class="form-group">
                    <label>Senha:</label>
                    <input type="password" id="password" required placeholder="Digite sua senha">
                </div>
                <button type="submit" class="btn">Entrar</button>
                <div id="loginError" style="color: red; margin-top: 15px; text-align: center; display: none;"></div>
            </form>
            <div class="developer-credit" style="margin-top: 30px; text-align: center;">
                <strong>💻 Desenvolvido por:</strong><br>
                Marcio Góes do Nascimento
            </div>
        </div>

        <!-- Main App -->
        <div id="app">
            <div class="container">
                <div class="header">
                    <h1>🤖 RAG Chatbot com Claude</h1>
                    <p>Sistema Inteligente de Consulta a Documentos com IA</p>
                    <div class="developer-credit">
                        <strong>💻 Desenvolvido por: Marcio Góes do Nascimento</strong><br>
                        Sistema RAG (Retrieval-Augmented Generation) com Anthropic Claude
                    </div>
                </div>
                
                <div class="user-info">
                    <div>
                        <span class="name" id="userName"></span><br>
                        <small id="userEmail"></small>
                    </div>
                    <button class="btn btn-danger" style="width: auto; padding: 8px 16px;" onclick="logout()">
                        🚪 Sair
                    </button>
                </div>
                
                <div class="main-content">
                    <div class="sidebar">
                        <div class="section">
                            <h2>📤 Upload de Documentos</h2>
                            <div class="upload-area" id="uploadArea">
                                <p>📁 Arraste arquivos aqui<br>ou clique para selecionar</p>
                                <input type="file" id="fileInput" multiple accept=".pdf,.docx,.txt,.xlsx,.pptx,.csv,.md">
                            </div>
                            <button class="btn" onclick="document.getElementById('fileInput').click()">
                                Selecionar Arquivos
                            </button>
                        </div>
                        
                        <div class="section">
                            <h2>📚 Documentos Carregados</h2>
                            <div class="stats">
                                <div class="stat-card">
                                    <div class="value" id="docCount">0</div>
                                    <div class="label">Documentos</div>
                                </div>
                                <div class="stat-card">
                                    <div class="value" id="chunkCount">0</div>
                                    <div class="label">Chunks</div>
                                </div>
                            </div>
                            <ul id="documentList"></ul>
                            <button class="btn btn-danger" onclick="clearAllDocuments()">
                                🗑️ Limpar Todos
                            </button>
                        </div>
                        
                        <div class="section">
                            <h2>📦 Exportar Dados</h2>
                            <div class="export-buttons">
                                <button class="btn btn-success" onclick="exportarJSON()">
                                    📄 JSON
                                </button>
                                <button class="btn btn-success" onclick="exportarCSV()">
                                    📊 CSV
                                </button>
                            </div>
                            <button class="btn btn-warning" onclick="exportarChromaDB()" style="margin-top: 10px;">
                                💾 Banco Vetorial
                            </button>
                        </div>
                    </div>
                    
                    <div class="chat-section">
                        <div class="section">
                            <h2>💬 Chat com IA</h2>
                            <div class="chat-container">
                                <div id="chatMessages">
                                    <div class="message bot">
                                        <strong>🤖 Claude (Assistente IA):</strong><br>
                                        Olá! Sou o Claude, um assistente de IA desenvolvido pela Anthropic. 
                                        Faça upload de documentos e pergunte qualquer coisa sobre eles. 
                                        Estou pronto para ajudar! 😊
                                    </div>
                                </div>
                                <div class="chat-input-area">
                                    <input type="text" id="chatInput" placeholder="Digite sua pergunta aqui..." 
                                           onkeypress="if(event.key==='Enter') sendMessage()">
                                    <button class="btn" onclick="sendMessage()">Enviar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <strong>💻 Sistema desenvolvido por: Marcio Góes do Nascimento</strong><br>
                    <small>RAG Chatbot v2.0 | Powered by Anthropic Claude & ChromaDB</small>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processando...</p>
            </div>
        </div>

        <script>
            let authToken = localStorage.getItem('authToken');
            
            // Verifica se está logado
            if (authToken) {
                checkAuth();
            }
            
            async function handleLogin(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const errorDiv = document.getElementById('loginError');
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('authToken', data.access_token);
                        localStorage.setItem('userName', data.user.nome);
                        localStorage.setItem('userEmail', data.user.email);
                        authToken = data.access_token;
                        
                        document.getElementById('loginScreen').style.display = 'none';
                        document.getElementById('app').style.display = 'block';
                        
                        document.getElementById('userName').textContent = data.user.nome;
                        document.getElementById('userEmail').textContent = data.user.email;
                        
                        await loadDocuments();
                    } else {
                        errorDiv.textContent = 'Usuário ou senha incorretos';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Erro ao conectar com servidor';
                    errorDiv.style.display = 'block';
                }
            }
            
            async function checkAuth() {
                try {
                    const response = await fetch('/me', {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    });
                    
                    if (response.ok) {
                        const user = await response.json();
                        document.getElementById('loginScreen').style.display = 'none';
                        document.getElementById('app').style.display = 'block';
                        
                        document.getElementById('userName').textContent = user.nome;
                        document.getElementById('userEmail').textContent = user.email;
                        
                        await loadDocuments();
                    } else {
                        logout();
                    }
                } catch (error) {
                    logout();
                }
            }
            
            function logout() {
                localStorage.removeItem('authToken');
                localStorage.removeItem('userName');
                localStorage.removeItem('userEmail');
                authToken = null;
                document.getElementById('loginScreen').style.display = 'block';
                document.getElementById('app').style.display = 'none';
            }
            
            function getAuthHeaders() {
                return {
                    'Authorization': `Bearer ${authToken}`
                };
            }
            
            // Upload de arquivos
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'));
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'));
            });
            
            uploadArea.addEventListener('drop', handleDrop);
            fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
            
            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                handleFiles(files);
            }
            
            async function handleFiles(files) {
                const loading = document.getElementById('loading');
                loading.classList.add('active');
                
                for (let file of files) {
                    await uploadFile(file);
                }
                
                await loadDocuments();
                loading.classList.remove('active');
            }
            
            async function uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        headers: getAuthHeaders(),
                        body: formData
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        addMessage('bot', `✅ Arquivo "${file.name}" processado com sucesso!`);
                    } else {
                        addMessage('bot', `❌ Erro ao processar "${file.name}": ${result.detail}`);
                    }
                } catch (error) {
                    addMessage('bot', `❌ Erro ao enviar "${file.name}": ${error.message}`);
                }
            }
            
            async function loadDocuments() {
                try {
                    const response = await fetch('/documents', {
                        headers: getAuthHeaders()
                    });
                    const docs = await response.json();
                    
                    const docList = document.getElementById('documentList');
                    docList.innerHTML = '';
                    
                    docs.forEach(doc => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <span>📄 ${doc.filename}</span>
                            <button onclick="deleteDocument('${doc.doc_id}')" style="background: #f5576c; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">🗑️</button>
                        `;
                        docList.appendChild(li);
                    });
                } catch (error) {
                    console.error('Erro ao carregar documentos:', error);
                }
                
                await loadStats();
            }
            
            async function loadStats() {
                try {
                    const response = await fetch('/stats', {
                        headers: getAuthHeaders()
                    });
                    const stats = await response.json();
                    
                    document.getElementById('docCount').textContent = stats.total_documents || 0;
                    document.getElementById('chunkCount').textContent = stats.total_chunks || 0;
                } catch (error) {
                    console.error('Erro ao carregar estatísticas:', error);
                }
            }
            
            async function deleteDocument(docId) {
                if (!confirm('Tem certeza que deseja remover este documento?')) return;
                
                try {
                    const response = await fetch(`/documents/${docId}`, {
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    });
                    
                    if (response.ok) {
                        addMessage('bot', '✅ Documento removido com sucesso!');
                        await loadDocuments();
                    }
                } catch (error) {
                    addMessage('bot', `❌ Erro ao remover documento: ${error.message}`);
                }
            }
            
            async function clearAllDocuments() {
                if (!confirm('Tem certeza que deseja remover TODOS os documentos?')) return;
                
                const loading = document.getElementById('loading');
                loading.classList.add('active');
                
                try {
                    const response = await fetch('/documents/clear', {
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    });
                    
                    if (response.ok) {
                        addMessage('bot', '✅ Todos os documentos foram removidos!');
                        await loadDocuments();
                    }
                } catch (error) {
                    addMessage('bot', `❌ Erro ao limpar documentos: ${error.message}`);
                }
                
                loading.classList.remove('active');
            }
            
            async function sendMessage() {
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                addMessage('user', message);
                input.value = '';
                
                const loading = document.getElementById('loading');
                loading.classList.add('active');
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...getAuthHeaders()
                        },
                        body: JSON.stringify({
                            message: message,
                            use_rag: true,
                            n_context_docs: 3
                        })
                    });
                    
                    const result = await response.json();
                    
                    let botResponse = result.response;
                    if (result.sources && result.sources.length > 0) {
                        botResponse += '<div class="sources"><strong>📚 Fontes:</strong><br>';
                        result.sources.forEach(source => {
                            botResponse += `• ${source.filename}<br>`;
                        });
                        botResponse += '</div>';
                    }
                    
                    addMessage('bot', botResponse);
                } catch (error) {
                    addMessage('bot', `❌ Erro ao processar mensagem: ${error.message}`);
                }
                
                loading.classList.remove('active');
            }
            
            function addMessage(type, content) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const prefix = type === 'user' ? '👤 Você' : '🤖 Claude (Assistente IA)';
                messageDiv.innerHTML = `<strong>${prefix}:</strong><br>${content}`;
                
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // Funções de Exportação
            async function exportarJSON() {
                const loading = document.getElementById('loading');
                loading.classList.add('active');
                
                try {
                    const response = await fetch('/export/json', {
                        headers: getAuthHeaders()
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'documentos_exportados.json';
                        a.click();
                        addMessage('bot', '✅ Exportação JSON concluída!');
                    }
                } catch (error) {
                    addMessage('bot', `❌ Erro ao exportar JSON: ${error.message}`);
                }
                
                loading.classList.remove('active');
            }
            
            async function exportarCSV() {
                const loading = document.getElementById('loading');
                loading.classList.add('active');
                
                try {
                    const response = await fetch('/export/csv', {
                        headers: getAuthHeaders()
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'documentos_exportados.csv';
                        a.click();
                        addMessage('bot', '✅ Exportação CSV concluída!');
                    }
                } catch (error) {
                    addMessage('bot', `❌ Erro ao exportar CSV: ${error.message}`);
                }
                
                loading.classList.remove('active');
            }
            
            async function exportarChromaDB() {
                addMessage('bot', '💡 O banco vetorial ChromaDB está localizado em: ./chroma_db/<br>Você pode copiar esta pasta para usar em outros projetos!');
            }
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(usuario_atual)):
    """Upload e processa um arquivo (rota protegida)"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in document_processor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {file_ext}"
            )
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        doc_data = document_processor.process_file(str(file_path), file.filename)
        
        doc_id = rag_engine.add_document(
            content=doc_data['content'],
            metadata={
                'filename': doc_data['filename'],
                'format': doc_data['format'],
                'size': doc_data['size'],
                'uploaded_by': current_user['username']
            }
        )
        
        file_path.unlink()
        
        return {
            'success': True,
            'doc_id': doc_id,
            'filename': file.filename,
            'message': f'Arquivo "{file.filename}" processado com sucesso!'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(usuario_atual)):
    """Endpoint de chat (rota protegida)"""
    try:
        response = chatbot.chat(
            user_message=request.message,
            use_rag=request.use_rag,
            n_context_docs=request.n_context_docs
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(current_user: dict = Depends(usuario_atual)):
    """Lista todos os documentos (rota protegida)"""
    try:
        documents = rag_engine.list_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user: dict = Depends(usuario_atual)):
    """Remove um documento (rota protegida)"""
    try:
        success = rag_engine.delete_document(doc_id)
        if success:
            return {'success': True, 'message': 'Documento removido com sucesso'}
        else:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/clear")
async def clear_all_documents(current_user: dict = Depends(usuario_atual)):
    """Remove todos os documentos (rota protegida)"""
    try:
        success = rag_engine.clear_all()
        if success:
            return {'success': True, 'message': 'Todos os documentos foram removidos'}
        else:
            raise HTTPException(status_code=500, detail="Erro ao limpar documentos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats(current_user: dict = Depends(usuario_atual)):
    """Retorna estatísticas do sistema (rota protegida)"""
    try:
        stats = rag_engine.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de Exportação

@app.get("/export/json")
async def exportar_json(current_user: dict = Depends(usuario_atual)):
    """Exporta todos os documentos para JSON"""
    try:
        results = rag_engine.collection.get()
        
        dados_exportados = {
            'exportado_por': current_user['nome'],
            'data_exportacao': datetime.now().isoformat(),
            'desenvolvedor': 'Marcio Góes do Nascimento',
            'total_documentos': len(set([m.get('doc_id') for m in results['metadatas']])),
            'total_chunks': len(results['ids']),
            'documentos': []
        }
        
        for i in range(len(results['ids'])):
            dados_exportados['documentos'].append({
                'id': results['ids'][i],
                'conteudo': results['documents'][i],
                'metadata': results['metadatas'][i] if results['metadatas'] else {}
            })
        
        export_path = EXPORT_DIR / f"export_{current_user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(dados_exportados, f, ensure_ascii=False, indent=2)
        
        return FileResponse(
            export_path,
            media_type='application/json',
            filename='documentos_exportados.json'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/csv")
async def exportar_csv(current_user: dict = Depends(usuario_atual)):
    """Exporta todos os documentos para CSV"""
    try:
        results = rag_engine.collection.get()
        
        export_path = EXPORT_DIR / f"export_{current_user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Conteudo', 'Arquivo', 'Formato', 'Chunk', 'Exportado_Por'])
            
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                writer.writerow([
                    results['ids'][i],
                    results['documents'][i],
                    metadata.get('filename', ''),
                    metadata.get('format', ''),
                    metadata.get('chunk_index', ''),
                    current_user['nome']
                ])
        
        return FileResponse(
            export_path,
            media_type='text/csv',
            filename='documentos_exportados.csv'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Verifica se o servidor está funcionando"""
    return {
        'status': 'healthy',
        'rag_engine': 'operational',
        'chatbot': 'operational',
        'desenvolvedor': 'Marcio Góes do Nascimento',
        'versao': '2.0.0'
    }

if __name__ == "__main__":
    print("🚀 Iniciando RAG Chatbot com Autenticação...")
    print("📡 Acesse: http://localhost:8000")
    print("\n💻 Desenvolvido por: Marcio Góes do Nascimento")
    print("\n⚙️  Configurações:")
    print(f"   - Banco vetorial: {rag_engine.persist_directory}")
    print(f"   - Modelo embeddings: {rag_engine.embeddings.model_name}")
    print(f"   - LLM Provider: {chatbot.llm_provider}")
    print("\n🔐 Credenciais padrão:")
    print("   - Usuário: admin | Senha: admin123")
    print("   - Usuário: marcio | Senha: marcio2024")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
