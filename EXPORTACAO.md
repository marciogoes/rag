# 📤 Guia de Exportação RAG - Parte 2

## 🔄 Exportação de Dados

### Uso:
```powershell
python exportar_dados.py
```

Isso cria:
- `documentos_exportados.json` - Todos os documentos em JSON
- `documentos_exportados.csv` - Todos os documentos em CSV

### Importar em outro sistema:

```python
import json

# Carregar os dados
with open('documentos_exportados.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Usar em seu chatbot
for doc in dados['documentos']:
    print(doc['conteudo'])
    print(doc['metadata'])
```

---

## 🤖 Opção 4: Integração com Plataformas No-Code

### A) Make.com / Integromat

**1. Configure um Webhook:**
- Crie um novo cenário no Make
- Adicione módulo "Webhooks"
- Use o endpoint: `http://localhost:8001/search`

**2. No Make:**
```
HTTP Module → POST Request
URL: http://localhost:8001/search
Body: {"query": "{{texto_do_usuario}}", "n_results": 3}
```

### B) Zapier

**1. Use "Webhooks by Zapier"**
**2. Configure:**
```
Method: POST
URL: http://localhost:8001/search
Data: query={{user_message}}&n_results=3
```

### C) Bubble.io

**1. API Connector:**
```
Name: RAG_Search
Use as: Data (GET)
URL: http://localhost:8001/search
Type: POST
Body: {"query": "<text>", "n_results": 3}
```

---

## 🔀 Opção 5: Migrar para Outro Banco Vetorial

### Pinecone:
```python
import pinecone
from rag_engine import RAGEngine

# Exportar do ChromaDB
rag = RAGEngine()
results = rag.collection.get()

# Importar para Pinecone
pinecone.init(api_key="sua-chave")
index = pinecone.Index("nome-do-index")

for i in range(len(results['ids'])):
    index.upsert(
        vectors=[(
            results['ids'][i],
            results['embeddings'][i],
            results['metadatas'][i]
        )]
    )
```

### Weaviate:
```python
import weaviate
from rag_engine import RAGEngine

client = weaviate.Client("http://localhost:8080")

# Exportar e importar
rag = RAGEngine()
results = rag.collection.get()

for i in range(len(results['ids'])):
    client.data_object.create({
        "content": results['documents'][i],
        "metadata": results['metadatas'][i]
    }, "Document")
```

---

## 🌍 Opção 6: Deploy na Nuvem

### Railway / Render / Fly.io

**1. Crie um `Procfile`:**
```
web: python api_consulta.py
```

**2. Deploy:**
```bash
git init
git add .
git commit -m "RAG API"
# Push para Railway/Render
```

**3. Use a URL pública:**
```
https://seu-app.railway.app/search
```

---

## 📊 Comparação de Métodos

| Método | Dificuldade | Flexibilidade | Requer Internet |
|--------|-------------|---------------|-----------------|
| Copiar ChromaDB | ⭐ Fácil | ⭐⭐ Média | ❌ Não |
| API Local | ⭐⭐ Média | ⭐⭐⭐ Alta | ❌ Não |
| Exportar JSON/CSV | ⭐ Fácil | ⭐⭐⭐ Alta | ❌ Não |
| API em Nuvem | ⭐⭐⭐ Difícil | ⭐⭐⭐ Alta | ✅ Sim |
| Outro Banco Vetorial | ⭐⭐⭐ Difícil | ⭐⭐⭐ Alta | Depende |

---

## 💡 Recomendação

**Para integração rápida:** Use a **API de Consulta** (`api_consulta.py`)
- Funciona com qualquer linguagem
- Mantém embeddings otimizados
- Fácil de integrar

**Para portabilidade total:** Use **Exportação JSON**
- Pode ser importado em qualquer sistema
- Formato universal
- Fácil de processar

---

## 🚀 Próximos Passos

**1. Testar a API:**
```powershell
python api_consulta.py
```

**2. Acessar documentação:**
```
http://localhost:8001/docs
```

**3. Fazer teste:**
```bash
curl -X POST "http://localhost:8001/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "teste", "n_results": 3}'
```

---

**Qual método você prefere usar?** 🤔
