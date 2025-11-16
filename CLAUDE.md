# 🤖 RAG Chatbot com Claude (Anthropic)

Sistema completo de RAG (Retrieval-Augmented Generation) usando **Claude** como modelo de linguagem.

## 🎯 O que mudou?

✅ **Antes:** OpenAI GPT  
✅ **Agora:** Anthropic Claude (Sonnet 4)  

### Vantagens do Claude:
- 🧠 Mais inteligente e contextual
- 📊 Melhor compreensão de documentos
- 💰 Custo-benefício superior
- 🌍 Janela de contexto maior (200K tokens)

## 📦 Instalação

### 1. Instalar a biblioteca Anthropic

```powershell
pip install anthropic==0.39.0
```

### 2. Obter Chave da API Anthropic

1. Acesse: https://console.anthropic.com/
2. Crie uma conta (se não tiver)
3. Vá em **API Keys**
4. Crie uma nova chave
5. Copie a chave

### 3. Configurar o arquivo .env

Crie um arquivo `.env` na raiz do projeto:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxx_sua_chave_aqui_xxx
```

**Importante:** Nunca compartilhe sua chave da API!

## 🚀 Como Usar

### Iniciar o servidor:

```powershell
cd "C:\Users\marci\OneDrive\Documentos\Projetos\rag"
.\venv\Scripts\activate
python main.py
```

### Acessar a interface:

Abra seu navegador em: **http://localhost:8000**

## 🔧 Compatibilidade

O sistema ainda mantém compatibilidade com OpenAI. Para usar GPT ao invés de Claude:

1. No arquivo `main.py`, linha 38, mude:
```python
chatbot = RAGChatbot(rag_engine=rag_engine, llm_provider="anthropic")
```

Para:
```python
chatbot = RAGChatbot(rag_engine=rag_engine, llm_provider="openai")
```

2. Configure `OPENAI_API_KEY` no `.env`

## 📋 Modelos Disponíveis

### Claude (Recomendado):
- `claude-sonnet-4-20250514` - Mais recente e poderoso (padrão)
- `claude-3-5-sonnet-20241022` - Versão anterior, ainda excelente
- `claude-3-haiku-20240307` - Mais rápido e econômico

### OpenAI (Opcional):
- `gpt-4` - Mais poderoso
- `gpt-3.5-turbo` - Mais rápido

## 💡 Recursos

### Upload de Documentos
- PDF, DOCX, TXT, XLSX, PPTX, CSV, MD
- Drag & drop na interface
- Processamento automático

### RAG (Retrieval-Augmented Generation)
- Busca semântica nos documentos
- Embeddings com sentence-transformers
- Armazenamento vetorial com ChromaDB

### Chatbot Inteligente
- Respostas baseadas nos documentos
- Citação de fontes
- Contexto preservado

## 🔍 API Endpoints

- `POST /upload` - Upload de documento
- `POST /chat` - Enviar mensagem
- `GET /documents` - Listar documentos
- `DELETE /documents/{id}` - Remover documento
- `DELETE /documents/clear` - Limpar todos
- `GET /stats` - Estatísticas do sistema
- `GET /health` - Status do servidor

## 📝 Exemplo de Uso via API

```python
import requests

# Upload
files = {'file': open('documento.pdf', 'rb')}
response = requests.post('http://localhost:8000/upload', files=files)

# Chat
chat_data = {
    'message': 'O que diz o documento sobre X?',
    'use_rag': True,
    'n_context_docs': 3
}
response = requests.post('http://localhost:8000/chat', json=chat_data)
print(response.json()['response'])
```

## 🐛 Troubleshooting

### Erro: "ANTHROPIC_API_KEY não configurada"
**Solução:** Crie o arquivo `.env` com sua chave da API

### Erro: "Biblioteca Anthropic não instalada"
**Solução:** Execute `pip install anthropic==0.39.0`

### Erro ao compilar ChromaDB
**Solução:** Instale o Windows SDK pelo Visual Studio Installer

## 📞 Suporte

Para mais informações sobre a API Anthropic:
- Documentação: https://docs.anthropic.com/
- Console: https://console.anthropic.com/
- Preços: https://www.anthropic.com/pricing

---

Desenvolvido com ❤️ usando FastAPI + Claude + ChromaDB
