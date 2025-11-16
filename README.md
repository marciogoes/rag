# 🤖 RAG Chatbot com Claude - Sistema Completo

**Desenvolvido por: Marcio Góes do Nascimento**

Sistema avançado de RAG (Retrieval-Augmented Generation) com autenticação e funcionalidades de exportação.

---

## ✨ Novidades da Versão 2.0

### 🔐 Sistema de Autenticação
- Login com usuário e senha
- Tokens JWT com validade de 8 horas
- Rotas protegidas
- Gerenciamento de sessão

### 📤 Funcionalidades de Exportação
- **Exportar JSON**: Todos os documentos em formato JSON
- **Exportar CSV**: Dados estruturados em planilha
- **Banco Vetorial**: ChromaDB portável

### 👨‍💻 Créditos do Desenvolvedor
- Assinatura em todas as páginas
- Informações no rodapé
- Metadados nos arquivos exportados

---

## 🚀 Instalação

### 1. Instalar Dependências

```powershell
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
```

### 2. Configurar Usuários

Edite o arquivo `config_usuarios.py` para adicionar/remover usuários:

```python
USUARIOS = {
    "admin": {
        "senha": "admin123",
        "nome": "Administrador",
        "email": "admin@rag.com"
    },
    "marcio": {
        "senha": "marcio2024",
        "nome": "Marcio Góes",
        "email": "marcio@rag.com"
    }
}
```

### 3. Iniciar o Servidor

```powershell
python main.py
```

Acesse: **http://localhost:8000**

---

## 🔑 Credenciais Padrão

**Usuário Administrador:**
- Usuário: `admin`
- Senha: `admin123`

**Usuário Desenvolvedor:**
- Usuário: `marcio`
- Senha: `marcio2024`

---

## 📋 Funcionalidades

### 🔐 Autenticação
- Login seguro com JWT
- Sessão persistente (8 horas)
- Logout automático ao expirar
- Proteção de todas as rotas sensíveis

### 📤 Upload de Documentos
- Arraste e solte arquivos
- Formatos: PDF, DOCX, TXT, XLSX, PPTX, CSV, MD
- Processamento automático
- Metadados do usuário que fez upload

### 💬 Chat com IA
- Integração com Claude (Anthropic)
- Respostas baseadas em documentos
- Citação de fontes
- Histórico de conversação

### 📊 Exportação de Dados

#### 1. JSON
Exporta todos os documentos com:
- Conteúdo completo
- Metadados
- Informações do exportador
- Créditos do desenvolvedor

**Formato:**
```json
{
  "exportado_por": "Nome do Usuário",
  "data_exportacao": "2024-11-16T12:00:00",
  "desenvolvedor": "Marcio Góes do Nascimento",
  "total_documentos": 10,
  "total_chunks": 50,
  "documentos": [...]
}
```

#### 2. CSV
Planilha com todas as informações:
- ID do chunk
- Conteúdo
- Arquivo original
- Formato
- Índice do chunk
- Quem exportou

#### 3. Banco Vetorial (ChromaDB)
Pasta `./chroma_db/` contém:
- Embeddings calculados
- Índice vetorial
- Metadados completos

**Como usar em outro projeto:**
```bash
# Copiar a pasta
xcopy /E /I chroma_db C:\outro\projeto\chroma_db
```

---

## 🔌 API Endpoints

### Autenticação

```
POST /login
Body: {"username": "admin", "password": "admin123"}
Response: {"access_token": "...", "token_type": "bearer"}
```

```
GET /me
Headers: Authorization: Bearer {token}
Response: {"username": "admin", "nome": "...", "email": "..."}
```

### Documentos

```
POST /upload
Headers: Authorization: Bearer {token}
File: documento.pdf
```

```
GET /documents
Headers: Authorization: Bearer {token}
```

```
DELETE /documents/{doc_id}
Headers: Authorization: Bearer {token}
```

### Chat

```
POST /chat
Headers: Authorization: Bearer {token}
Body: {
  "message": "Qual o conteúdo do documento?",
  "use_rag": true,
  "n_context_docs": 3
}
```

### Exportação

```
GET /export/json
Headers: Authorization: Bearer {token}
Response: documentos_exportados.json
```

```
GET /export/csv
Headers: Authorization: Bearer {token}
Response: documentos_exportados.csv
```

---

## 🛡️ Segurança

### Autenticação JWT
- Tokens com expiração
- HMAC SHA-256
- Rotas protegidas

### Configuração de Produção

**⚠️ IMPORTANTE:** Antes de colocar em produção:

1. **Mude a SECRET_KEY** em `config_usuarios.py`:
```python
SECRET_KEY = "gere-uma-chave-forte-aqui-use-secrets.token_urlsafe(32)"
```

2. **Use senhas fortes**:
```python
# Não use senhas simples como "admin123"
# Use senhas complexas: "S3nh@Fo rt3!2024"
```

3. **Configure HTTPS**:
```python
# Em produção, use SSL/TLS
uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

---

## 📦 Estrutura de Arquivos

```
rag/
├── main.py                    # Aplicação principal com autenticação
├── auth.py                    # Sistema de autenticação JWT
├── config_usuarios.py         # Configuração de usuários
├── chatbot.py                 # Lógica do chatbot com Claude
├── rag_engine.py              # Motor RAG com ChromaDB
├── document_processor.py      # Processamento de documentos
├── requirements.txt           # Dependências
├── .env                       # Chave da API Anthropic
├── chroma_db/                 # Banco vetorial (portável)
├── uploads/                   # Arquivos temporários
└── exports/                   # Arquivos exportados
```

---

## 🔧 Troubleshooting

### Erro: "python-jose não instalado"
```powershell
pip install python-jose[cryptography]==3.3.0
```

### Erro: "passlib não instalado"
```powershell
pip install passlib[bcrypt]==1.7.4
```

### Erro: "Token inválido"
- Faça logout e login novamente
- Verifique se o token não expirou (8 horas)

### Erro: "SECRET_KEY não encontrada"
- Verifique o arquivo `config_usuarios.py`
- A SECRET_KEY deve estar definida

---

## 🌟 Recursos Avançados

### Adicionar Novo Usuário

Edite `config_usuarios.py`:

```python
USUARIOS = {
    "novo_usuario": {
        "senha": "senha_segura_aqui",
        "nome": "Nome Completo",
        "email": "email@exemplo.com"
    }
}
```

### Integrar com Outros Sistemas

Use a API de exportação para integrar:

```python
import requests

# Login
response = requests.post('http://localhost:8000/login', json={
    'username': 'admin',
    'password': 'admin123'
})

token = response.json()['access_token']

# Buscar documentos
headers = {'Authorization': f'Bearer {token}'}
docs = requests.get('http://localhost:8000/documents', headers=headers)

# Exportar JSON
export = requests.get('http://localhost:8000/export/json', headers=headers)
with open('backup.json', 'wb') as f:
    f.write(export.content)
```

---

## 📞 Suporte

**Desenvolvedor:** Marcio Góes do Nascimento

**Tecnologias Utilizadas:**
- FastAPI
- Anthropic Claude (Sonnet 4)
- ChromaDB
- LangChain
- JWT Authentication
- Python 3.12

---

## 📄 Licença

Sistema desenvolvido por **Marcio Góes do Nascimento**.

---

## 🎯 Próximas Funcionalidades

- [ ] Backup automático agendado
- [ ] Múltiplos níveis de permissão
- [ ] Integração com Active Directory
- [ ] Dashboard de analytics
- [ ] API de webhook para notificações
- [ ] Suporte a mais modelos de IA

---

**Versão:** 2.0.0  
**Última Atualização:** Novembro 2024  
**Desenvolvido por:** Marcio Góes do Nascimento
